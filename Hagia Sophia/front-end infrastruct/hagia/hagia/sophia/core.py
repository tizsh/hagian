#Original core

import requests
from bs4 import BeautifulSoup
import time
import re
import time
from .models import Bookmark, Folder
from PIL import Image
import uuid

basic_url_pattern = "([a-zA-Z0-9]*[\.*])*[a-zA-Z0-9]+[\.][a-zA-Z]+([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"
proper_url_pattern = "((http|https)\:\/\/)+[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"

DESCRIPTION_MAX = 100
TITLE_MAX = 200
DEFAULT_FOLDER_ID = 0 


def match_url(pattern, string):
	p = re.compile( pattern )
	m = p.match(string)
	if m:
	    return True
	else:
	    return False

def get_image(soup):
	img = soup.find_all("img", src = True)
	try:
		for i in img:
			try:
				response = requests.get(i['src'], stream=True)
				raw_content = response.raw.read()
				print("url"+ i['src']+ "   SIZE : "+str(len(raw_content))+ "KB")	
				if(len(raw_content) >= 20000):				
					img = Image.open(requests.get(i['src'], stream = True).raw)
					extension = ""
					if((i['src']).find(".jpg") != -1):
						print("Image is jpg!")
						extension += ".jpg"
					elif((i['src']).find(".gif") != -1):
						extension += ".gif"
					else:
						extension = None
					img_name = str(uuid.uuid4())
					print("extension "+ extension)
					print("img_name " + img_name)
					if(extension != None):
						print("img_name " + img_name)
						print("extension "+ extension)
						img.save("sophia/assets/"+img_name+extension)
						return img_name
			except Exception as ea:
				print(ea)
	except Exception as e:
		return str(e)
		print(e)
	return None

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
		folder = Folder.objects.get(f_id = primary_key)
		if(folder == None):
			return False
		else:
			return True
	except Exception as e:
		print(str(e) + " ...error from folder_exist")
		return None
	return False

def add_bookmark_to_db(url, title = None, relevant_img = None, description = None, folder_primary_key = DEFAULT_FOLDER_ID):
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
	if(relevant_img == None):
		relevant_img = "nooooooImg"
	fol = Folder.objects.get(f_id = folder_primary_key)
	bm = Bookmark(url = url, title = title, description = description, relevant_img = relevant_img, folder_name = fol)
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


def standarize(link):
	if (match_url(proper_url_pattern, link) == False and match_url(basic_url_pattern,link) == True):
		return "http://"+link


def add_online(link, folder_primary_key = None):

	if (match_url(proper_url_pattern, link) == False and match_url(basic_url_pattern,link) == True):
		link = "http://"+link

	if(match_url(proper_url_pattern, link) == False and match_url(basic_url_pattern,link) == False and ignore_invalid_urls == False):
		return False

	if(len(link) < 2):
		return False
	try:
		page = requests.get(link)
		soup = BeautifulSoup(page.text, 'html.parser')
		img_name = get_image(soup)
		title = soup.title.text
		description = get_description(soup)

		if(folder_exist(folder_primary_key) == True and folder_primary_key != None):
			add_bookmark_to_db(url = link, title = title, description = description, relevant_img = img_name , folder_primary_key = folder_primary_key)
		else:
			add_bookmark_to_db(url = link, title = title, description = description, relevant_img = img_name , folder_primary_key = DEFAULT_FOLDER_ID)			
		return True
	except Exception as e:
		return str(e)
		print("Error in add_online")

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
			add_bookmark_to_db(url = link, folder_primary_key = DEFAULT_FOLDER_ID)
			return True

	except Exception as e:
		print("Offline_add did not work")

	return False


def add_bookmark(link,folder_primary_key = None):
	link = normalize(link)
	try:
		return add_online(link, folder_primary_key = 1)

	except Exception as e:
		print("add_online failed... trying offline method")

	try:
		return offline_add(link, folder_primary_key = 1)
	
	except Exception as e:
		print("offline_add failed... returning false")

	return False

def delete_folder(folder_primary_key, delete_inner_bookmarks = False):
	try:

		if(delete_inner_bookmarks == True):
			bm = Bookmark.objects.filter(folder_name = Folder.objects.get(f_id = folder_primary_key))
			bm.delete()
			bm.save()

		else:
			bm = Bookmark.objects.filter(folder_name = Folder.objects.get(f_id = folder_primary_key))
			bm.update(folder_name = Folder.objects.get(f_id = DEFAULT_FOLDER_ID))

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

def edit_bookmark_title(bookmark_pk,new_title):
	try:
		bm = Bookmark.objects.filter(pk = bookmark_pk)
		bm.update(title = new_title)
		return True
	except Exception as e:
		return str(e)
		print("Error in edit_bookmark_title!")

	return False

def edit_bookmark_description(bookmark_pk, new_description):
	try:
		bm = Bookmark.objects.filter(pk = bookmark_pk)
		bm.update(description = new_description)
		return True
	except Exception as e:
		return str(e)
		print("Error in edit_bookmark_title!")

	return False

def edit_bookmark_folder(bookmark_pk,new_folder_pk):
	try:
		bm = Bookmark.objects.filter(pk = bookmark_pk)
		bm.update(folder_name = folder_pk)
		return True
	except Exception as e:
		return str(e)
		print("Error in edit_bookmark_title!")

	return False

def edit_folder_name(folder_pk, new_name):
	try:
		fol = Folder.objects.filter(pk = folder_pk)
		fol.update(name = new_name)
		return True
	except Exception as e:
		return str(e)
		print("Error in edit_bookmark_title!")

	return False


def edit_folder_name(folder_pk, new_parent_pk):
	try:
		fol = Folder.objects.filter(pk = folder_pk)
		fol.update(parent_id = new_parent_pk)
		return True
	except Exception as e:
		return str(e)
		print("Error in edit_bookmark_title!")

	return False


