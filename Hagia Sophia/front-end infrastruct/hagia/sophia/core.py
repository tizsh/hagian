#Original core

import requests
from bs4 import BeautifulSoup
import time
import re
import time
from .models import Bookmark, Folder


basic_url_pattern = "([a-zA-Z0-9]*[\.*])*[a-zA-Z0-9]+[\.][a-zA-Z]+([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"
proper_url_pattern = "((http|https)\:\/\/)+[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"

DESCRIPTION_MAX = 100
TITLE_MAX = 20
DEFAULT_FOLDER_ID = 0 


def match_url(pattern, string):
	p = re.compile( pattern )
	m = p.match(string)
	if m:
	    return True
	else:
	    return False


def get_description(soup):
	results = soup.find_all("meta", content = True)
	try:
		for meta in results:
			if(str((meta.get("name"))).lower() == "description"):
				if(len(((meta.get('content')).replace("'", "")).replace('"','')) > 255):
					d = ((meta.get('content')).replace("'", "").replace('"',''))[:255 - 4] + "..."
					return d
				return (meta.get('content')).replace("'", "").replace('"','')
	except Exception as e:
		print(e)

	return ""


def folder_exist(primary_key):
	try:
		folder = Folder.objects.get(pk = primary_key)
		if(folder == None):
			return False
		else:
			return True
	except Exception as e:
		print(str(e) + " ...error from folder_exist")
		return None
	return False


def add_bookmark_to_db(url, title = None, description = None, folder_primary_key = DEFAULT_FOLDER_ID):
	if(title == None):
		title = url

	if(description == None):
		description = ""

	if(len(description) > DESCRIPTION_MAX - 3):
		description = description[:DESCRIPTION_MAX - 3] + "..."

	if(len(title) > TITLE_MAX):
		title = title[:TITLE_MAX - 3] + "..."
	
	if(len(description) > DESCRIPTION_MAX):
		description = description[:DESCRIPTION_MAX - 3] + "..."

	fol = Folder.objects.get(pk = folder_primary_key)
	bm = Bookmark(url = url, title = title, description = description, folder_name = fol)
	bm.save()


def add_folder_to_db(folder_name):
	fol = Folder(name = folder_name)
	fol.save()


def normalize(l):
	try:
		#remove white spaces in link
		l = l.replace(" ", "%20")

		#replace ' from link
		l = l.replace("'", "")
		l = l.replace('"', "")

	except Exception as e:
		print("Normalization failed. Returning original subroutine")

	return l


def add_online(link, folder_primary_key = None):

	if (match_url(proper_url_pattern, link) == False and match_url(basic_url_pattern,link) == True):
		link = "http://"+link

	if(match_url(proper_url_pattern, link) == False and match_url(basic_url_pattern,link) == False and ignore_invalid_urls == False):
		return False

	if(len(link) < 2):
		return False

	page = requests.get(link)
	soup = BeautifulSoup(page.text, 'html.parser')
	title = soup.title.text
	description = get_description(soup)
	
	if(folder_exist(folder_primary_key) == True and folder_primary_key != None):
		add_bookmark_to_db(url = link, title = title, description = description, folder_primary_key = folder_primary_key)
		return True

	if(folder_exist(folder_primary_key) == False and folder_primary_key != None):
		add_folder_to_db(folder_primary_key)
		add_bookmark_to_db(url = link, title = title, description = description, folder_primary_key = folder_primary_key)
		return True

	else:
		add_bookmark_to_db(url = link, title = title, description = description, folder_primary_key = DEFAULT_FOLDER_ID)
		return True

	return False


def offline_add(link, folder_primary_key = None):

	if (match_url(proper_url_pattern, link) == False and match_url(basic_url_pattern,link) == True):
		link = "http://"+link

	if(match_url(proper_url_pattern, link) == False and match_url(basic_url_pattern,link) == False and ignore_invalid_urls == False):
		return False

	if(len(link) < 2):
		return False

	try:
		if(folder_exist(folder_primary_key) == True and folder_primary_key != None):
			add_bookmark_to_db(url = link, folder_primary_key = folder_primary_key)
			return True
		else:
			add_bookmark_to_db(url = link)
			return True

	except Exception as e:
		print("Offline_add did not work")

	return False


def add_bookmark(link,folder_primary_key = None):
	link = normalize(link)
	try:
		return add_online(link, folder_primary_key)

	except Exception as e:
		print("add_online failed... trying offline method")

	try:
		return offline_add(link, folder_primary_key)
	
	except Exception as e:
		print("offline_add failed... returning false")

	return False


def delete_folder(folder_primary_key, delete_inner_bookmarks = False):
	try:

		if(delete_inner_bookmarks == True):
			bm = Bookmark.objects.filter(folder_name = Folder.objects.get(pk = folder_primary_key))
			bm.delete()
			bm.save()

		else:
			bm = Bookmark.objects.filter(folder_name = Folder.objects.get(pk = folder_primary_key))
			bm.update(folder_name = Folder.objects.get(pk = DEFAULT_FOLDER_ID))
			bm.save()

		folder = Folder.objects.filter(name = fol)
		folder.delete()
		folder.save()

		return True
	except Exception as e:
		raise (e)

	return False


def delete_bookmark(link):
	try:
		bm = Bookmark.objects.filter(url = link)
		bm.delete()
		bm.save()
		return True
	except Exception as e:
		print(e)

	return False


