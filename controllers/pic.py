
from flask import *
from extensions import mysql, check_session
from datetime import datetime

pic = Blueprint('pic', __name__, template_folder='views', url_prefix='/j89pws9vn291/pa4/pic')

def is_picid_valid(id):
	result = True
	cur = mysql.connection.cursor()
	try:
		row = cur.execute("SELECT picid FROM Photo WHERE picid=%s", (id,))
		if row == 0:
			result = False
	except:
		print "Cannot find the picid = " + id + "!"
	finally:
		cur.close()
		return result

def is_username_valid(user):
	result = True
	cur = mysql.connection.cursor()
	try:
		row = cur.execute("SELECT username FROM User WHERE username=%s", (user,))
		if row == 0:
			result = False
	except:
		print "Cannot find the username = " + user + "!"
	finally:
		cur.close()
		return result

def has_user_already_liked_pic(id, user):
	result = True
	cur = mysql.connection.cursor()
	try:
		row = cur.execute("SELECT date FROM Favorite WHERE picid=%s AND username=%s", (id, user))
		if row == 0:
			result = False
	except:
		print "The user " + user + " has not liked the pic " + id + "!"
	finally:
		cur.close()
		return result

def get_pic_favorite_info(id):
	latest_favorites = None
	num_favorites = 0
	cur = mysql.connection.cursor()
	try:
		num_favorites = cur.execute("SELECT picid FROM Favorite WHERE picid=%s", (id,))
		row = cur.execute("SELECT username FROM Favorite WHERE picid=%s and date=(SELECT MAX(date) FROM Favorite WHERE picid=%s)", (id, id))
		if row > 0:
			latest_favorites = cur.fetchone()
	except:
		print "Count picid query or lastest favorites query is wrong!"
	finally:
		cur.close()

	result = []
	if (latest_favorites is not None):
		result.append(latest_favorites[0])
	else:
		result.append("")
	result.append(num_favorites)

	return result;

@pic.route('', methods=['GET'])
def pic_route():
	pic_id = None
	username = None
	prev_id = []
	next_id = []
	id = None

	pic_id = request.args.get('id', None)

	if pic_id is not None:
		next_url = None
		options = {
			"prev": True,
			"next": True
		}
		sensitive = False
		cur = mysql.connection.cursor()
		try:
			cur.execute("SELECT url FROM Photo WHERE picid=%s", (pic_id,))
			pic_url = cur.fetchone()
			cur.execute("SELECT sequencenum, albumid, caption FROM Contain WHERE picid=%s", (pic_id,))
			seq_tuple = cur.fetchone()
			cur.execute("SELECT username, access FROM Album WHERE albumid=%s",(seq_tuple[1],))
			album_info =  cur.fetchone()

			if 'username' in session and check_session():
				username = session['username']
				if album_info[1] == 'private':
					rows_count = cur.execute("SELECT username FROM AlbumAccess WHERE albumid=%s AND username=%s",(seq_tuple[1], username))
					if username !=album_info[0] and rows_count == 0:
						options = {
							"edit": False,
							"login": True,
							"refill": True
						}
						print "Access denied!"
						return render_template("user.html", options = options)
				sensitive = True
			else:
				if album_info[1] == 'private':
					cur.close()
					options = {
						"edit": False,
						"login": True,
						"refill": True
					}
					print "Access denied!"
					return render_template("user.html", options=options, prev_url='/j89pws9vn291/pa4/pic?id=' + pic_id)

			id = seq_tuple[1]
			cur.execute("SELECT MAX(sequencenum) FROM Contain WHERE albumid=%s", (seq_tuple[1],))

			max_seq = cur.fetchone()
			seq_num = int(seq_tuple[0])
			prev_seq = seq_num - 1
			next_seq = seq_num + 1
			
			if seq_num == 1:
				prev_seq = None
			if seq_num >= max_seq[0]:
				next_seq = None
			if prev_seq == None and next_seq == None:
				# print "pass"
				options = {
					"prev": False,
					"next": False
				}
			elif prev_seq is None:
				cur.execute("SELECT picid FROM Contain WHERE albumid=%s and sequencenum=%s", (seq_tuple[1], next_seq))
				next_id = cur.fetchone()
				options = {
					"prev": False,
					"next": True
				}
			elif next_seq == None:
				cur.execute("SELECT picid FROM Contain WHERE albumid=%s and sequencenum=%s", (seq_tuple[1], prev_seq))
				prev_id = cur.fetchone()
				options = {
					"prev": True,
					"next": False
				}
			else:
				cur.execute("SELECT picid FROM Contain WHERE albumid=%s and sequencenum=%s", (seq_tuple[1], next_seq))
				next_id = cur.fetchone()
				cur.execute("SELECT picid FROM Contain WHERE albumid=%s and sequencenum=%s", (seq_tuple[1], prev_seq))
				prev_id = cur.fetchone()
		except:
			print "Some query inside is wrong!"
		finally:
			cur.close()

		result = get_pic_favorite_info(pic_id)
		latest_favorites = result[0]
		num_favorites = result[1]

		session['lastactivity'] = datetime.now()
		return render_template("pic.html", pic_url=pic_url, prev_id=prev_id, next_id=next_id, options=options, id=id, user_name=username, 
			caption=seq_tuple[2], pic_id=pic_id, latest_favorites=latest_favorites, num_favorites=num_favorites, sensitive=sensitive)
	else:
		return abort(404)

@pic.route('/caption', methods=['GET'])
def pic_caption_get():
    picid = request.args.get('id', None)
    if picid == None:
    	response = json.jsonify(error='You did not provide an id parameter.', status=404)
    	response.status_code = 404
    	return response

    query = "SELECT caption FROM Contain WHERE picid='%s';" % (picid)
    cur = mysql.connection.cursor()
    cur.execute(query)
    results = cur.fetchall()
    caption = ""
    if len(results) > 0:
        caption = results[0][0]
        if caption == None:
        	caption = ""
    else:
        response = json.jsonify(error='Invalid id parameter. The picid does not exist.', status=422)
        response.status_code = 422
        return response
    return json.jsonify(caption=caption)

@pic.route('/caption', methods=['POST'])
def pic_caption_post():
    req_json = request.get_json()

    picid = req_json.get('id', None)
    caption = req_json.get('caption', None)
    if picid is None and caption is None:
        response = json.jsonify(error='You did not provide an id and caption parameter.', status=404)
        response.status_code = 404
        return response
    if picid is None:
        response = json.jsonify(error='You did not provide an id parameter.', status=404)
        response.status_code = 404
        return response
    if caption is None:
        response = json.jsonify(error='You did not provide a caption parameter.', status=404)
        response.status_code = 404
        return response

    try:
    	query_picid = "SELECT picid, albumid FROM Contain WHERE picid='%s';" % (picid)
        query = "UPDATE Contain SET caption='%s' WHERE picid='%s';" % (caption, picid)
        cur = mysql.connection.cursor()
        rows_count = cur.execute(query_picid)
        if rows_count == 0:
        	raise Exception
        query_picid_tuple = cur.fetchone()
        albumid = query_picid_tuple[1]
        query_lastupdate = "UPDATE Album SET lastupdated=NOW() WHERE albumid='%s';" % (albumid)
        cur.execute(query_lastupdate)
    	cur.execute(query)
    	mysql.connection.commit()
    except:
        response = json.jsonify(error='Invalid id. The picid does not exist.', status=422)
        response.status_code = 422
        return response
    finally:
    	cur.close()
    response = json.jsonify(caption=caption, status=201)
    response.status_code = 201
    return response

@pic.route('/favorites', methods=['GET'])
def pic_favorites_get():
	picid = None
	try:
 		req_json = request.get_json()
 		picid = req_json.get('id')
 	except:
 		picid = request.args.get('id', None)

 	if picid is None:
 		response = json.jsonify(error='You did not provide an id parameter.', status=404)
 		response.status_code = 404
 		return response
 	elif is_picid_valid(picid) is False:
 		response = json.jsonify(error='Invalid id parameter. The picid does not exist.', status=422)
 		response.status_code = 422
 		return response
 	else:
 		result = get_pic_favorite_info(picid)
 		latest_favorite = result[0]
 		num_favorites = result[1]

		response = json.jsonify(id=picid, num_favorites=num_favorites, latest_favorite=latest_favorite)
		response.status_code = 200
		return response


@pic.route('/favorites', methods=['POST'])
def pic_favorites_post():
 	req_json = request.get_json()
 	picid = req_json.get('id')
 	latest_favorite = req_json.get('username')

 	if picid is None and latest_favorite is None:
 		response = json.jsonify(error='You did not provide an id and username parameter.', status=404)
 		response.status_code = 404
 		return response
 	elif picid is None and latest_favorite is not None:
 		response = json.jsonify(error='You did not provide an id parameter.', status=404)
 		response.status_code = 404
 		return response
 	elif picid is not None and latest_favorite is None:
 		response = json.jsonify(error='You did not provide a username parameter.', status=404)
 		response.status_code = 404
 		return response
 	elif is_picid_valid(picid) is False:
 		response = json.jsonify(error='Invalid id. The picid does not exist.', status=422)
 		response.status_code = 422
 		return response
 	elif is_username_valid(latest_favorite) is False:
 		response = json.jsonify(error='Invalid username. The username does not exist.', status=422)
 		response.status_code = 422
 		return response
 	elif has_user_already_liked_pic(picid, latest_favorite) is True:
 		response = json.jsonify(error='The user has already favorited this photo.', status=403)
 		response.status_code = 403
 		return response
 	else:
 		response = None
 		cur = mysql.connection.cursor()
 		try:
 			cur.execute("INSERT INTO Favorite (picid, username, date) VALUES (%s, %s, NOW())", (picid, latest_favorite))
			mysql.connection.commit()
			response = json.jsonify(id=picid, status=201)
			response.status_code = 201
 		except:
 			print "Cannot like the photo."
 			response = json.jsonify(error='Inserting a new record into Favorite fails.', status=400)
 			response.status_code = 400
 		finally:
 			cur.close()
 			
 		return response

