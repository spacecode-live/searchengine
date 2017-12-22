
from flask.ext.mysqldb import MySQL
from flask.ext.mail import Mail
from flask import session
import datetime

mysql = MySQL()
mail = Mail()

def check_session():
	validate_time = datetime.datetime.now() - session['lastactivity']
	if validate_time > datetime.timedelta(seconds=300):
		session.clear()
		return False
	else:
		return True