
from flask import *
from extensions import mysql, check_session
from datetime import datetime
import requests
import json

main = Blueprint('main', __name__, template_folder='views', url_prefix='/j89pws9vn291/pa6')

class PageInfo(object):
    def __init__(self, pageId, pageUrl, imgUrl, categories, summary):
    	self.id = pageId
    	self.url = pageUrl
        self.imgUrl = imgUrl
        self.category = categories
        self.summary = summary

@main.route('/')
def main_route():
    if 'username' in session and check_session() is True:
		user = session['username']
		options = {
			"logged_in": True
		}
		session['lastactivity'] = datetime.now()
		titles = []
		cur = mysql.connection.cursor()
		try:
			cur.execute("SELECT albumid, title, access FROM Album WHERE access='public' OR username=%s OR albumid IN (SELECT albumid FROM AlbumAccess WHERE username=%s)",(user,user))
			titles = cur.fetchall()
		except:
			print "Get info of all public albums query is wrong!"
		finally:
			cur.close()
		return render_template("index.html", options=options, user=user, titles=titles) 
    else:
		options = {
			"logged_in": False
		}
		return render_template("index.html", options=options) 

@main.route('/logout')
def logout_route():
	session.clear()
	return redirect('/j89pws9vn291/pa4')

@main.route('/live')
def live_route():
    return send_file('./views/live.html')

@main.route('/search', methods=['GET']) 
def search_route():
	search_result = True
	pageList = []
	if request.method == 'GET':
		query = request.args.get('query', None)
		wVal = request.args.get('w-value')
		if query == None:
			search_result = False
		else:
			try:
				result = requests.get('http://eecs485-09.eecs.umich.edu:6387/search?q='+query+'&'+'w='+wVal)
				json_data = json.loads(result.text)
				json_data = json_data['hits']
				for queryhit in json_data:
					hitId = queryhit['id']
					cur = mysql.connection.cursor()
					try:
						cur.execute("SELECT page_url FROM imageUrls WHERE id=%s",(hitId,))
						url = cur.fetchone()
						if url is None:
							final_url = "https://en.wikipedia.org/wiki?curid=" + hitId
						else:
							final_url = url[0]
						cur.execute("SELECT image_url FROM imageUrls WHERE id=%s",(hitId,))
						imgurl = cur.fetchone()
						if imgurl is None:
							final_imgurl = ""
						else:
							final_imgurl = imgurl[0]
						cur.execute("SELECT category FROM categories WHERE id=%s",(hitId,))
						categories = cur.fetchall()
						cur.execute("SELECT summary FROM infobox WHERE id=%s",(hitId,))
						summary = cur.fetchone()
						if summary is None:
							final_summary = ""
						else:
							final_summary = summary[0]
						pageInfo = PageInfo(hitId, final_url, final_imgurl, categories, final_summary)
						pageList.append(pageInfo)
					except:
						print "Get page info query is wrong!"
					finally:
						cur.close()
			except:
				print "Cannot find words in the query!"
	size_pageList = len(pageList)
	if size_pageList > 10:
		pageList = pageList[:10]
	return render_template("search.html", pages=pageList, size=size_pageList, result=search_result)
