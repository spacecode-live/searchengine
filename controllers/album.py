
from flask import *

from extensions import mysql, check_session
import hashlib
from datetime import datetime
import os

UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = set(['png','jpg','bmp','gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

album = Blueprint('album', __name__, template_folder='views', url_prefix='/j89pws9vn291/pa4/album')

@album.route('/edit', methods=['GET'])
def album_edit_route():
	album_edit_id = request.args.get('id', None)
	if album_edit_id is not None:
		picids=[]
		users_with_access = []

		cur = mysql.connection.cursor()
		try: 
			cur.execute("SELECT title, access, username FROM Album WHERE albumid=%s", (album_edit_id,))
			album_info = cur.fetchone()

			if 'username' in session and check_session():
				username = session['username']
				if username == album_info[2]:
					if album_info[1] == "private":
						options = {
							"edit": True,
							"private": True,
							"sensitive": True
						}
					elif album_info[1] == "public":
						options = {
							"edit": True,
							"private": False,
							"sensitive": True
						}
				else:
					options = {
						"edit": False,
						"login": True,
						"refill": True
					}
					print "Access denied!"
					return render_template("user.html", options=options,  prev_url='/j89pws9vn291/pa4/album/edit?id='+album_edit_id)
			else:
				options = {
					"edit": False,
					"login": True,
					"refill": True
				}
				print "Access denied!"
				return render_template("user.html", options=options, prev_url='/j89pws9vn291/pa4/album/edit?id='+album_edit_id)
		except:
			print "Get info of an album query is wrong!"
		finally:
			cur.close()

		cur = mysql.connection.cursor()
		try:
			cur.execute("SELECT username FROM AlbumAccess WHERE albumid=%s", (album_edit_id,))
			users_with_access = cur.fetchall()

			cur.execute("SELECT Photo.picid, Photo.url, Photo.date, Contain.caption FROM Photo, Contain WHERE Photo.picid=Contain.picid AND albumid=%s ORDER BY Contain.sequencenum", (album_edit_id,))
			picids = cur.fetchall()
		except:
			print "Get info of a user access query or get info of a photo query is wrong!"
		finally:
			cur.close()

		return render_template("album.html", options=options, picids=picids, albumid=album_edit_id, album_info=album_info, users_with_access=users_with_access)
	else:
		return abort(404)

@album.route('/edit', methods=['POST'])
def album_edit_route_post():
	op = request.form.get('op', None)
	if op is not None:
		albumid = request.form.get('albumid')
		picids=[]
		users_with_access=[]

		cur = mysql.connection.cursor()
		try:
			cur.execute("SELECT title, access, username FROM Album WHERE albumid=%s", (albumid,))
			album_info = cur.fetchone()
		except:
			print "Get info of an album query is wrong!"
		finally:
			cur.close()

		if op == "add":
			_file = request.files['filepath']
			if _file and allowed_file(_file.filename):
				filename = _file.filename.rsplit('.', 1)[0]
				format = _file.filename.rsplit('.', 1)[1]
				# new_filename = _file.filename.rsplit('.', 1)[0]
				# filename.update(new_filename.encode('utf-8'))
				picid = filename
				url = '/pictures/' + picid + '.' + format
				_file.save(UPLOAD_FOLDER + url)

				cur = mysql.connection.cursor()
				try:
					cur.execute("SELECT sequencenum FROM Contain WHERE albumid=%s", (albumid,))
					test_seq = cur.fetchall()
					if len(test_seq) == 0:
						new_seq = 1
					else:
						cur.execute("SELECT MAX(sequencenum) FROM Contain WHERE albumid=%s", (albumid,))
						maxsequence = cur.fetchone()
						new_seq = maxsequence[0] + 1
					cur.execute("INSERT INTO Contain (albumid, picid, sequencenum) VALUES (%s, %s, %s)", (albumid, picid, new_seq))
					cur.execute("INSERT INTO Photo (picid, url, format, date) VALUES (%s, %s, %s, NOW())", (picid, url, format))
					mysql.connection.commit()
				except:
					print "Some query inside is wrong!"
				finally:
					cur.close()

		if op == "delete":
			picid = request.form.get('picid')
			url = ""

			cur = mysql.connection.cursor()
			try:
				cur.execute("SELECT url FROM Photo WHERE picid=%s", (picid,))
				url = cur.fetchone()

				#update seqnum
				cur.execute("SELECT sequencenum FROM Contain WHERE albumid=%s AND picid=%s", (albumid, picid))
				del_seq = cur.fetchone()
				cur.execute("SELECT picid,sequencenum FROM Contain WHERE sequencenum>%s", (del_seq[0],))
				pic_need_to_decre = cur.fetchall()
				if len(pic_need_to_decre) == 0:
					print "this is the last pic"
				else:
					for pic_decre in pic_need_to_decre:
						cur.execute("UPDATE Contain SET sequencenum=%s WHERE picid=%s AND albumid=%s", (pic_decre[1]-1, pic_decre[0], albumid))
					mysql.connection.commit()
				#update seqnum

				cur.execute("DELETE FROM Contain WHERE albumid=%s AND picid=%s", (albumid, picid))
				mysql.connection.commit()
			except:
				print "Update sequence num query is wrong!"
			finally:
				cur.close()
		
			os.remove(UPLOAD_FOLDER + url[0])

		if op == "title_edit":
			new_title = request.form.get('new_title')
			cur = mysql.connection.cursor()
			try:
				cur.execute("UPDATE Album SET title=%s WHERE albumid=%s", (new_title, albumid))
				mysql.connection.commit()
			except:
				print "Update album title query is wrong!"
			finally:
				cur.close()

		if op == "access_edit":
			cur = mysql.connection.cursor()
			try:
				if album_info[1] == 'public':
					cur.execute("UPDATE Album SET access='private' WHERE albumid=%s", (albumid,))
				else:
					cur.execute("UPDATE Album SET access='public' WHERE albumid=%s", (albumid,))
					cur.execute("DELETE FROM AlbumAccess WHERE albumid=%s", (albumid,))
				mysql.connection.commit()
			except:
				print "Update access of an album query is wrong!"
			finally:
				cur.close()

		if op == "add_new_user_with_access":
			new_user_with_access = request.form.get('new_user_with_access')
			cur = mysql.connection.cursor()
			try:
				rows_count = cur.execute("SELECT username FROM User WHERE username=%s",(new_user_with_access,))
				if rows_count > 0:
					cur.execute("INSERT INTO AlbumAccess(albumid, username) VALUES (%s, %s)", (albumid, new_user_with_access));
					mysql.connection.commit()
			except:
				print "Add new access of a user query is wrong!"
			finally:
				cur.close()

		if op == "revoke":
			revoked_user = request.form.get('username')
			cur = mysql.connection.cursor()
			try:
				cur.execute("DELETE FROM AlbumAccess WHERE albumid=%s AND username=%s", (albumid, revoked_user))
				mysql.connection.commit()
			except:
				print "Delete access of a user query is wrong!"
			finally:
				cur.close()

		cur = mysql.connection.cursor()
		cur.execute("SELECT title, access, username FROM Album WHERE Album.albumid=%s", (albumid,))
		album_info = cur.fetchone()
		cur.execute("SELECT Photo.picid, Photo.url, Photo.date, Contain.caption FROM Photo, Contain WHERE Photo.picid=Contain.picid and albumid=%s ORDER BY Contain.sequencenum", (albumid,))
		picids = cur.fetchall()

		cur.execute("UPDATE Album SET lastupdated=NOW() WHERE albumid=%s",(albumid,))
		mysql.connection.commit()

		if 'username' in session and check_session():
			username = session['username']
			if username == album_info[2]:
				if album_info[1] == "private":
					cur.execute("SELECT username FROM AlbumAccess WHERE albumid=%s", (albumid,))
					users_with_access = cur.fetchall()
					options = {
						"edit": True,
						"private": True,
						"sensitive": True
					}
				elif album_info[1] == "public":
					options = {
						"edit": True,
						"private": False,
						"sensitive": True
					}
			else:
				options = {
					"edit": False,
					"login": True,
					"refill": True
				}
				print "Access denied!"
				return render_template("user.html", options=options)
		else:
			options = {
				"edit": False,
				"login": True,
				"refill": True
			}
			print "Access denied!"
			return render_template("user.html", options=options, prev_url='/j89pws9vn291/pa4/album?id=' + albumid)
			
		cur.close()
		session['lastactivity'] = datetime.now()
		return render_template("album.html", options=options, albumid=albumid, picids=picids, album_info=album_info, users_with_access=users_with_access)
	else:
		return abort(404)

@album.route('', methods=['GET'])
def album_route():
	album_id = request.args.get('id', None)
	if album_id is not None:
		picids=[]
		album_owner=[]
		cur = mysql.connection.cursor()

		cur.execute("SELECT title, access, username FROM Album WHERE albumid=%s", (album_id,))
		album_info = cur.fetchone()

		if 'username' in session and check_session():
			username = session['username']
			if album_info[1] == 'private':
				rows_count = cur.execute("SELECT username FROM AlbumAccess WHERE albumid=%s AND username=%s", (album_id, username))
				if rows_count > 0 or username == album_info[2]:
					options = {
						"edit": False,
						"private": True,
						"sensitive": True
					}
				else:
					options = {
						"edit": False,
						"login": True,
						"refill": True
					}
					print "access denied!"
					return render_template("user.html", options=options)
			else:
				options = {
					"edit": False,
					"private": False,
					"sensitive": True
				}
		else:
			if album_info[1] == 'private':
				options = {
					"edit": False,
					"login": True,
					"refill": True
				}
				print "access denied!"
				return render_template("user.html", options=options, prev_url='/j89pws9vn291/pa4/album?id='+album_id)
			else:
				options = {
					"edit": False,
					"private": False,
					"sensitive": False
				}

		cur.execute("SELECT Photo.picid, Photo.url, Photo.date, Contain.caption FROM Photo,Contain WHERE Photo.picid=Contain.picid and albumid=%s ORDER BY Contain.sequencenum", (album_id,))
		picids = cur.fetchall()

		cur.close()
		session['lastactivity'] = datetime.now()
		return render_template("album.html", options=options, picids=picids,albumid=album_id,album_info=album_info)
	else:
		return abort(404)
