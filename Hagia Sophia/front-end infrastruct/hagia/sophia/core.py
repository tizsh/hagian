#All of the core functionality of Sophiax. 

import requests
from bs4 import BeautifulSoup
import time
import re
import time
from .models import Bookmark, Folder




basic_url_pattern = "([a-zA-Z0-9]*[\.*])*[a-zA-Z0-9]+[\.][a-zA-Z]+([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"
proper_url_pattern = "((http|https)\:\/\/)+[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"




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

def add_bookmark(link,folder_name = None, ignore_invalid_urls = False):
	link.replace(" ", "%20")
	link.replace("'", "")

	if(len(link) > 0 ):
		if (match_url(proper_url_pattern, link) == False and match_url(basic_url_pattern,link) == True and ignore_invalid_urls == False):
			link = "http://"+link
		if(match_url(proper_url_pattern, link) == False and match_url(basic_url_pattern,link) == False and ignore_invalid_urls == False):
			return False

		try:
			print("the upmost try is executing")
			page = requests.get(link)
			print("first milestone")

			soup = BeautifulSoup(page.text, 'html.parser')
			title = soup.title.text
			description = get_description(soup)

			if(title == None or title =="" or title == []):
				title = link.replace("'", "")
				title = link.replace('"', "")

			if(len(title) > 254):
				title = title[:254] + "..."

			if(len(description) > 254):
				description = description[:248] + "..."

			if(folder_exist(folder_name) == True and folder_name != None):
				fol = Folder.objects.get(name = folder_name)
				bm = Bookmark(url = link, title = title, description = description, folder_name = fol)
				bm.save()
			if(folder_exist(folder_name) == False and folder_name != None):
				fol = Folder(name = folder_name)
				fol.save()
				bm = Bookmark(url = link, title = title, description = description, folder_name = fol)
				bm.save()
			else:
				fol = Folder.objects.get(name = "///none///")	
				bm = Bookmark(url = link, title = title, description = description, folder_name = fol)
				bm.save()

			return True

		except Exception as e:
			raise e

	try:
		if(folder_exist(folder_name) == False and folder_name != None):
			fol = Folder(name = folder_name)
			fol.save()
			bm = Bookmark(url = link, title = link, folder_name = fol)
			bm.save()
		if(folder_exist(folder_name) == True and folder_name != None):
			fol = Folder.objects.get(name = folder_name)
			bm = Bookmark(url = link, title = link, folder_name = fol)
			bm.save()
		else:
			fol = Folder.objects.get(name = "///none///")	
			bm = Bookmark(url = link, title = link, folder_name = fol)
			bm.save()
		return True
	
	except Exception as e:
		print(e)

	return False




def delete_link(link):
	try:
		db = MySQLdb.connect(host="localhost",    # your host, usually localhost
		                   user="admin",         # your username
		                   passwd="admin",  # your password
		                   db="hagia")        # name of the data base
		x = db.cursor()
		x.execute("""DELETE FROM bookmarks WHERE url = '{0}'""".format(link))
		db.commit()
		return True
	except Exception as e:
		print(e)

	return False


def create_folder(folder_name):
	try:
		db = MySQLdb.connect(host="localhost",    # your host, usually localhost
				                   user="admin",         # your username
				                   passwd="admin",  # your password
				                   db="hagia")        # name of the data base
		x = db.cursor()		
		if(folder_exist(db,folder_name) == False):
			x.execute("""INSERT INTO folders(name) VALUES ('{0}')""".format(folder_name))
			db.commit()
			return True
	except Exception as e:
		print(e)

	return False		


def delete_folder(folder_name):
	try:
		db = MySQLdb.connect(host="localhost",    # your host, usually localhost
		                   user="admin",         # your username
		                   passwd="admin",  # your password
		                   db="hagia")        # name of the data base
		x = db.cursor()
		if(folder_exist(db,folder_name) == True):
			x.execute("""INSERT INTO folders(name) VALUES ('{0}')""".format(folder_name))
			db.commit()

			return True
	except Exception as e:
		print(e)

	return False


