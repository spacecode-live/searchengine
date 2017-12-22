
from flask import *

from datetime import datetime
from extensions import mysql, check_session

import os
UPLOAD_FOLDER = 'static' 
albums = Blueprint('albums', __name__, template_folder='views', url_prefix='/j89pws9vn291/pa4/albums')

@albums.route('/edit', methods=['GET'])
def albums_edit_route():
	titles = []
	if 'username' in session:
		if check_session() == False:
			options = {
				"edit": False,
				"login": True
			}
			return render_template("user.html", options=options, prev_url='/j89pws9vn291/pa4/albums/edit')
		else:
			username = session['username']
			cur = mysql.connection.cursor()

			try:
				cur.execute("SELECT albumid, title, access FROM Album WHERE username=%s", (username,))
				titles = cur.fetchall()
			except:
				print "Get title query is wrong!"
			finally:
				cur.close()

			options = {
				"edit": True,
				"sensitive": True
			}
			session['lastactivity'] = datetime.now()
			return render_template("albums.html", options=options, titles=titles, username=username)
	else:
		return abort(404)

@albums.route('/edit', methods=['POST'])
def albums_edit_route_post():
	if 'username' in session and check_session():
		op = request.form.get('op', None)
		if op is not None:
			titles = []
			if op == "delete":
				albumid = request.form.get('albumid')

				cur = mysql.connection.cursor()
				try:
					
					#delete the pics related to this album
					cur.execute("SELECT picid FROM Contain WHERE albumid=%s",(albumid,))
					picid_need_remove = cur.fetchall()
					for picid_remove in picid_need_remove:
						cur.execute("SELECT url FROM Photo WHERE picid=%s",(picid_remove[0],))
						url_remove = cur.fetchone()
						os.remove(UPLOAD_FOLDER+url_remove[0])

					cur.execute("SELECT username FROM Album WHERE albumid=%s",(albumid,))
					username = cur.fetchone()
					cur.execute("DELETE FROM Album WHERE albumid=%s", (albumid,))
					mysql.connection.commit()
					cur.execute("SELECT albumid, title, access FROM Album WHERE username=%s",(username[0],))
					titles = cur.fetchall()
				except:
					print "Some query inside is wrong!"
				finally:
					cur.close()

			if op == "add":
				username = request.form.get('username')
				title = request.form.get('title')
				access = request.form.get('access')
				cur = mysql.connection.cursor()
				try:
					cur.execute("INSERT INTO Album (title, created, lastupdated, username, access) VALUES (%s, NOW(), NOW(), %s, %s)",(title, username, access))
					mysql.connection.commit()
					cur.execute("SELECT albumid, title, access FROM Album WHERE username=%s",(username,))
					titles = cur.fetchall()
				except:
					print "Insert new album record is wrong! \n Get info of the album query is wrong!"
				finally:
					cur.close()

			options = {
				"edit": True,
				"sensitive": True
			}
			session['lastactivity'] = datetime.now()
			return render_template("albums.html", options=options, username=username, titles=titles)
		else:
			return abort(404)
	else:
		options = {
			"edit": False,
			"login": True
		}
		return render_template("user.html", options=options, prev_url='/j89pws9vn291/pa4/albums/edit')

@albums.route('', methods=['GET'])
def albums_route():
	if 'username' in session:
		if check_session() == False:
			options = {
				"edit": False,
				"login": True
			}
			return render_template("user.html", options=options, prev_url='/j89pws9vn291/pa4/albums')
		else:
			username = session['username']
			titles = []

			cur = mysql.connection.cursor()
			try:
				cur.execute("SELECT albumid, title, access FROM Album WHERE username=%s", (username,))
				titles = cur.fetchall()
			except:
				print "Get info of an album query is wrong!"
			finally:
				cur.close()

			options = {
				"edit": False,
				"sensitive": True
			}
			session['lastactivity'] = datetime.now()
			return render_template("albums.html", options=options, titles=titles, username=username)
	else:
		titles = []
		cur = mysql.connection.cursor()
		try:
			cur.execute("SELECT albumid, title, access FROM Album WHERE access='public'")
			titles = cur.fetchall()
		except:
			print "Get info of all public albums query is wrong!"
		finally:
			cur.close()

		options = {
			"edit": False,
			"sensitive": False
		}
		return render_template("albums.html", options=options, titles=titles)
