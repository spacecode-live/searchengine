from datetime import datetime
from collections import namedtuple
import copy

from flask import *
from extensions import mysql

api = Blueprint('api', __name__, template_folder='views', url_prefix='/j89pws9vn291/pa4')

Pic = namedtuple('Pic', ['picid', 'url', 'format', 'date'])
Favorite = namedtuple('Favorite', ['favoriteid', 'picid', 'username', 'date'])
Comment = namedtuple('Comment', ['commentid', 'picid', 'message', 'username', 'date'])
Contain = namedtuple('Contain', ['albumid', 'picid', 'caption', 'sequencenum'])
User = namedtuple('User', ['username', 'firstname', 'lastname', 'email'])

## Referenced from application
def execute(query):
	cur = mysql.connection.cursor()
	cur.execute(query)
	return cur.fetchall()

def update(query):
	cursor = mysql.connection.cursor()
	cursor.execute(query)
	mysql.connection.commit()
	return cursor.lastrowid


def get_prev_picid(albumid, sequencenum):
	query = "SELECT picid FROM Contain WHERE albumid =%d AND sequencenum < %d ORDER BY sequencenum DESC" %(albumid, sequencenum)
	results = execute(query)
	prevpicid = None
	if len(results) > 0:
		prevpicid = results[0][0]
	return prevpicid

def get_next_picid(albumid, sequencenum):
	query = "SELECT picid FROM Contain WHERE albumid=%d AND sequencenum>%d ORDER BY sequencenum ASC;" %(albumid, sequencenum)
	results = execute(query) 
	nextpicid = None
	if len(results) > 0:
		nextpicid = results[0][0]
	return nextpicid

def get_pic_by_id(picid):
	query = "SELECT picid, url, format, date FROM Photo WHERE picid='%s'" % (picid)
	results = execute(query)
	if len(results) > 0:
		pic = Pic(*results[0])
		return pic
	else:
		raise RecordNotFound(resource_type='Pic', source={"pointer": "data/attributes/picid"})

def get_favorite_by_id(favoriteid):
	query = "SELECT favoriteid, picid, username, date FROM Favorite WHERE favoriteid='%s'" % (favoriteid)
	results = execute(query)
	if len(results) > 0:
		favorite = Favorite(*results[0])
		return favorite
	else:
		raise RecordNotFound(resource_type="Favorite", source={"pointer": "data/attributes/id"})

def get_favorites_by_picid(picid):
	query = "SELECT favoriteid, picid, username, date FROM Favorite WHERE picid='%s'" % (picid)
	results = execute(query)
	favorites = []
	if len(results) > 0:
		favorites = [Favorite(*result) for result in results]
	return favorites

def get_comment_by_id(commentid):
	query = "SELECT commentid, picid, message, username, date FROM Comment WHERE commentid='%d'" % (commentid)
	results = execute(query)
	if len(results) > 0:
		comment = Comment(*results[0])
		return comment
	else:
		raise RecordNotFound(resource_type='Comment', source={"pointer": "data/attributes/id"})

def insert_comment(picid, message, username):
	query = "INSERT INTO Comment (picid, message, username) VALUES ('%s', '%s', '%s')" % (picid, message, username)
	try:
		commentid = update(query)
	except Exception:
		raise InsertFailed(resource_type='Comment', source={"pointer": "data/attributes/picid", 
															"pointer": "data/attributes/message",
															"pointer": "data/attributes/username"})
	return commentid

def update_caption(picid, caption):
	query = "UPDATE Contain SET caption='%s' WHERE picid='%s'" % (caption, picid)
	try:
		application.update(query)
	except Exception as e:
		print e
		raise UpdateFailed(resource_type='Pic', source={"pointer": "data/attributes/picid",
														"pointer": "data/attributes/caption"})

def get_comments_by_picid(picid):
	query = "SELECT commentid, picid, message, username, date FROM Comment WHERE picid='%s'" % (picid)
	results = execute(query)
	comments = []
	if len(results) > 0:
		comments = [Comment(*result) for result in results]
		return comments
	return comments

def get_contain_by_picid(picid):
	query = "SELECT albumid, picid, caption, sequencenum FROM Contain WHERE picid='%s'" % (picid)
	results = execute(query)
	if len(results) > 0:
		contain = Contain(*results[0])
		return contain
	else:
		raise RecordNotFound(resource_type='Contain', source={"pointer": "data/attributes/picid"})

def get_user_by_username(username):
	query = "SELECT username, firstname, lastname, email FROM User WHERE username='%s'" % (username)
	results = execute(query)
	if len(results) > 0:
		user = User(*results[0])
		return user
	else:
		raise RecordNotFound(resource_type='User', source={"pointer": "data/attributes/username"})

class JSONAPIException(Exception):

	def __init__(self, title, resource_type, message, status_code, source):
		self.status_code = status_code
		self.title = title
		self.resource_type = resource_type
		self.message = message
		self.status_code = status_code
		self.source = source
		super(JSONAPIException, self).__init__(self.to_json())

	def to_json(self):
		error = dict(status=self.status_code, title=self.title, source=self.source, detail=self.message) 
		return error

class RecordNotFound(JSONAPIException):

	def __init__(self, resource_type, source):
		super(RecordNotFound, self).__init__(title="Resource Not Found", resource_type=resource_type, 
			message="Resource not found for %s. Please verify you specified a valid id." % (resource_type),
			status_code=422, source=source)

class InsertFailed(JSONAPIException):

	def __init__(self, resource_type, source):
		super(InsertFailed, self).__init__(resource_type=resource_type, source=source, 
			title="Insert failed",
			message="Could not insert %s. Please verify correctness of your request." % (resource_type),
			status_code=422)

class UpdateFailed(JSONAPIException):

	def __init__(self, resource_type, source):
		super(UpdateFailed, self).__init__(resource_type=resource_type, source=source, 
			title="Update failed",
			message="Could not update %s. Please verify correctness of your request." % (resource_type),
			status_code=422)


class PicJSONAPI(object):

	def __init__(self, pic, favorites, comments, contain):
		self.pic = pic
		self.favorites = favorites
		self.comments = comments
		self.contain = contain

	def attributes(self):
		prevpicid = get_prev_picid(albumid=self.contain.albumid, sequencenum=self.contain.sequencenum)
		nextpicid = get_next_picid(albumid=self.contain.albumid, sequencenum=self.contain.sequencenum)
		attributes = {
			"picurl": self.pic.url,
			"prevpicid": prevpicid,
			"nextpicid": nextpicid,
			"caption": self.contain.caption	
		}
		return attributes

	def favorites_data(self):
		data = [{"id": favorite.favoriteid, "type": "favorites"} for favorite in self.favorites]
		return data

	def comments_data(self):
		data = [{"id": comment.commentid, "type": "comments"} for comment in self.comments]
		return data

	def relationships(self):
		relationships = {}

		favorites = self.favorites_data()
		if len(favorites) > 0:
			relationships["favorites"] = { "data": favorites }

		comments = self.comments_data()
		if len(comments) > 0:
			relationships["comments"] = { "data": comments }

		if not relationships:
			return None

		return relationships

	def to_json(self):
		data = {
				"type": "pics",
				"id": self.pic.picid,
				"attributes": self.attributes()
			}

		relationships = self.relationships()
		if relationships is not None:
			data["relationships"] = relationships
		return { "data": data }

@api.route('/pics/<picid>', methods=['GET'])
def pics(picid):

	try:
		pic = get_pic_by_id(picid)
		favorites = get_favorites_by_picid(picid)
		comments = get_comments_by_picid(picid)
		contain = get_contain_by_picid(picid)
	except RecordNotFound as e:
		response = json.jsonify(errors=[e.to_json()])
		response.status_code=404
		return response

	pic = PicJSONAPI(pic, favorites, comments, contain)
	data = pic.to_json()
	return json.jsonify(**data)

@api.route('/pics/<picid>', methods=['PATCH'])
def patch_caption(picid):
	try:
		data = request.get_json(force=True)["data"]
		caption = data["attributes"]["caption"]
		update_caption(picid, caption)
	except JSONAPIException as e:
		response = json.jsonify(errors=[e.to_json()])
		response.status_code = 422

	response = json.jsonify(data=data)
	response.status_code = 201
	return response


@api.route('/favorites/<int:id>')
def favorites(id):
	
	try:
		favorite = get_favorite_by_id(id)
	except RecordNotFound as e:
		response = json.jsonify(errors=[e.to_json()])
		response.status_code = 404
		return response

	data = {
		"type": "favorites",
		"id": id,
		"attributes": {
			"username": favorite.username,
			"datetime": favorite.date.isoformat()
		}
	}
	return json.jsonify(data=data)

def malformed_request():
	error = {
				"status": "400",
				"title": "Bad Request",
				"detail": "Your request could not be parsed. Please verify it is a valid JSON object."
			}
	return error

def comment_to_jsonapi(comment):
	rv = {
			"type": "comments",
			"id": comment.commentid
		}
	attributes = comment._asdict()
	attributes["date"] = attributes["date"].isoformat()
	del attributes["commentid"]
	rv["attributes"] = attributes
	return rv

@api.route('/comments/<int:commentid>', methods=['GET'])
def get_comment(commentid):
	try:
		comment = get_comment_by_id(commentid)
		comment = comment_to_jsonapi(comment)
	except RecordNotFound as e:
		response = json.jsonify(errors=[e.to_json()])
		response.status_code = e.status_code
		return response

	return json.jsonify(data=comment)

@api.route('/comments', methods=['POST'])
def post_comment():
	try:
		data = request.get_json(force=True)["data"]
		picid = data["relationships"]["pic"]["data"]["id"]
		username = data["attributes"]["username"]
		message = data["attributes"]["message"]
		date = data["attributes"]["message"]
		commentid = insert_comment(picid, message, username)
		data["id"] = commentid
	except JSONAPIException as e:
		response = json.jsonify(errors=[e.to_json()])
		response.status_code = 422

	response = json.jsonify(data=data)
	response.status_code = 201
	return response

@api.route('/users/<username>')
def get_user(username):
	try:
		user = get_user_by_username(username)
	except RecordNotFound as e:
		response = json.jsonify(errors=[e.to_json()])
		response.status_code = e.status_code
		return response

	data = {
		"type": "user",
		"id": username,
		"attributes": {
			"username": username,
			"firstname": user.firstname,
			"lastname": user.lastname
		}
	}
	return json.jsonify(data=data)