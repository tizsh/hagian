#Original core

import requests
from bs4 import BeautifulSoup
import time
import re
import time
from .models import Bookmark, Folder



#these are constants 

basic_url_pattern = "([a-zA-Z0-9]*[\.*])*[a-zA-Z0-9]+[\.][a-zA-Z]+([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"
proper_url_pattern = "((http|https)\:\/\/)+[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"

DESCRIPTION_MAX = 100
TITLE_MAX = 20
DEFAULT_FOLDER = "///none///"

# ignore_invalid_urls = True

#these are constants


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


def folder_exist(name1):
	try:
		name1 =	name1.replace("%20", " ")
		folder = Folder.objects.get(name = name1)
		if(folder == None):
			return False
		else:
			return True
	except Exception as e:
		print(str(e) + " ...error from folder_exist")
		return None
	return False


def add_bookmark_to_db(url, title = None, description = None, folder_name = DEFAULT_FOLDER):
	if(title == None):
		title = url

	if(description == None):
		description = ""

	if(len(description) > DESCRIPTION_MAX - 3):
		description = description[:DESCRIPTION_MAX - 3] + "..."

	if(len(title) > TITLE_MAX):
		title = title[:TITLE_MAX - 3] + "..."

	if(description == None):
		description = ""
	
	if(len(description) > DESCRIPTION_MAX):
		description = description[:DESCRIPTION_MAX - 3] + "..."

	fol = Folder.objects.get(name = folder_name)
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


def add_online(link, folder_name = None):

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
	
	if(folder_exist(folder_name) == True and folder_name != None):
		add_bookmark_to_db(url = link, title = title, description = description, folder_name = folder_name)
		return True

	if(folder_exist(folder_name) == False and folder_name != None):
		add_folder_to_db(folder_name)
		add_bookmark_to_db(url = link, title = title, description = description, folder_name = folder_name)
		return True

	else:
		add_bookmark_to_db(url = link, title = title, description = description, folder_name = DEFAULT_FOLDER)
		return True

	return False


def offline_add(link, folder_name = None):

	if (match_url(proper_url_pattern, link) == False and match_url(basic_url_pattern,link) == True):
		link = "http://"+link

	if(match_url(proper_url_pattern, link) == False and match_url(basic_url_pattern,link) == False and ignore_invalid_urls == False):
		return False

	if(len(link) < 2):
		return False

	try:
		if(folder_exist(folder_name) == True and folder_name != None):
			add_bookmark_to_db(url = link, folder_name = folder_name)
			return True

		if(folder_exist(folder_name) == False and folder_name != None):
			add_folder_to_db(folder_name)
			add_bookmark_to_db(url = link, folder_name = folder_name)
			return True

		else:
			add_bookmark_to_db(url = link)
			return True

	except Exception as e:
		print("Offline_add did not work")

	return False



def add_bookmark(link,folder_name = None):
	link = normalize(link)
	try:
		return add_online(link, folder_name)

	except Exception as e:
		print("add_online failed... trying offline method")

	try:
		delete_bookmark("http://hello.com/fuckniggers101")
		return offline_add(link, folder_name)
	
	except Exception as e:
		print("offline_add failed... returning false")

	return False


### Remember that bookmark's url are not unique! To precisely delete the correct

def delete_folder(fol, delete_inner_bookmarks = False):
	try:

		if(delete_inner_bookmarks == True):
			bm = Bookmark.objects.filter(folder_name = Folder.objects.get(name = fol))
			bm.delete()
			bm.save()

		else:
			bm = Bookmark.objects.filter(folder_name = Folder.objects.get(name = fol))
			bm.update(folder_name = Folder.objects.get(name = fol))
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




















