
from flask import *
from flask.ext.mail import Message
import string
import random

from datetime import datetime
from extensions import mysql, check_session, mail

user = Blueprint('user', __name__, template_folder='views', url_prefix='/j89pws9vn291/pa4/user')

def pswd_generator(size=7, chars = string.ascii_uppercase + string.digits + string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(size)) + '007'

def send_email(recipient, firstname, username):
	msg = Message('Congratulations for Your Register', sender='eecs485group87@gmail.com', recipients=[recipient])
	msg.body = 'Dear ' + firstname + ', \n\n You have just registered the Online Photo Album Service successfully. Your user name is ' + username + '. \n\nThanks for using our service. \nTeam EECS485Group87'
	mail.send(msg)

def send_pswd_rest_email(recipient, firstname, new_pswd):
	msg = Message('Reset Your Password', sender='eecs485group87@gmail.com', recipients=[recipient])
	msg.body = 'Dear ' + firstname + ', \n\n You have just reset your password of the Online Photo Album Service successfully. Your new password is ' + new_pswd + '. \n\nThanks for using our service. \nTeam EECS485Group87'
	mail.send(msg)

def check_username(username):
	cur = mysql.connection.cursor()
	try:
		rows_count = cur.execute("SELECT username FROM User WHERE username=%s", (username,))
	except:
		print "Check username query is wrong!"
	finally:
		cur.close()

	if rows_count > 0:
		return True
	else:
		return False

@user.route('', methods=['GET', 'POST'])
def user_route():
	if request.method == 'POST':
		user_name = request.form.get('user_name', None)
		first_name = request.form.get('first_name', None)
		last_name = request.form.get('last_name', None)
		email = request.form.get('email', None)
		password = request.form.get('password', None)
		confirmPassword = request.form.get('confirmPassword', None)

		if password == confirmPassword: 
			if check_username(user_name) is False:
				cur = mysql.connection.cursor()
				try:
					cur.execute("INSERT INTO User VALUES (%s, %s, %s, %s, %s)", (user_name, first_name, last_name, password, email))
					mysql.connection.commit()
				except:
					print "Insert new user query is wrong!"
				finally:
					cur.close()

				send_email(email, first_name, user_name)
				options = {
					"edit": False,
					"login": True,
					"refill": False
				}
			else:
				options = {
					"edit": False,
					"login": False,
					"refill": True
				}
		else:
			options = {
				"edit": False,
				"login": False,
				"refill": True
			}
		return render_template("user.html", options=options)
	else:
		if 'username' in session and check_session() is True:
			session['lastactivity'] = datetime.now()
			return redirect('/j89pws9vn291/pa4/user/edit')
		else:	
			options = {
				"edit": False,
				"login": False,
				"refill": False
			}
			return render_template("user.html", options=options)

@user.route('/edit', methods=['GET', 'POST'])
def user_edit_route():
		if 'username' in session:
			if check_session() is False:
				options = {
					"edit": False,
					"login": True,
					"refill": True
				}
				return render_template("user.html", options=options, prev_url='/j89pws9vn291/pa4/user/edit')
			else:
				username = session['username']
				session['lastactivity'] = datetime.now()
				if request.method == 'POST':
					first_name = request.form.get('first_name', None)
					last_name = request.form.get('last_name', None)
					email = request.form.get('email', None)
					password = request.form.get('password', None)
					confirmPassword = request.form.get('confirmPassword', None)

					if password == confirmPassword:
						cur = mysql.connection.cursor()
						try:
							cur.execute("UPDATE User SET firstname=%s, lastname=%s, password=%s, email=%s WHERE username=%s", (first_name, last_name, password, email, username))
							mysql.connection.commit()
						except:
							print "Update existing user query is wrong!"
						finally:
							cur.close()
					else:
						cur = mysql.connection.cursor()
						try:
							cur.execute("SELECT firstname, lastname, email FROM User WHERE username=%s", (username,))
							name_and_email = cur.fetchone()
							options = {
								"edit": True,
								"login": False,
								"refill": False
							}
							return render_template("user.html", options=options, name_and_email=name_and_email)
						except:
							print "Insert new user query is wrong!"
						finally:
							cur.close()
				else:
					cur = mysql.connection.cursor()
					try:
						cur.execute("SELECT firstname, lastname, email FROM User WHERE username=%s", (username,))
						name_and_email = cur.fetchone()
						options = {
							"edit": True,
							"login": False,
							"refill": False
						}
						return render_template("user.html", options=options, name_and_email=name_and_email)
					except:
						print "Insert new user is wrong!"
					finally:
						cur.close()

			options = {
				"edit": False,
				"login": True,
				"refill": False
			}
			return render_template("user.html", options=options)

		else:
			options = {
				"edit": False,
				"login": True,
				"refill": False
			}
			return render_template("user.html", options=options, prev_url='/j89pws9vn291/pa4/user/edit')


@user.route('/login', methods=['POST','GET'])
def user_login_route():
	options = {
		"edit": False,
		"login": True,
		"refill": False
	}

	if request.method == 'POST':
		username = request.form.get('user_name', None)
		password = request.form.get('password', None)
		prev_url = request.form.get('prev_url', None)

		cur = mysql.connection.cursor()
		try:
			rows_count = cur.execute("SELECT password FROM User WHERE username=%s",(username,))
			if rows_count == 0:
				options = {
					"edit": False,
					"login": True,
					"refill": False
				}
				return render_template("user.html", options=options)
			real_password = cur.fetchone()
		except:
			print "Get password from corresponding user query is wrong!"
		finally:
			cur.close()

		if password == real_password[0]:
			session['username'] = username
			session['lastactivity'] = datetime.now()
			if prev_url == '' or prev_url == None:
				return redirect('/j89pws9vn291/pa4')
			else:
				return redirect(prev_url)
		else:
			options = {
					"edit": False,
					"login": True,
					"refill": False
				}
			return render_template("user.html", options=options)
	else:
		return render_template("user.html", options=options)

@user.route('/passwordReset', methods=['POST','GET'])
def user_passwordReset_route():
	if request.method == 'POST':
		user_name = request.form.get('user_name', None)
		new_pswd = pswd_generator()

		cur = mysql.connection.cursor()
		try:
			cur.execute("SELECT firstname, email FROM User WHERE username=%s", (user_name,))
			firstname_email = cur.fetchone()
			send_pswd_rest_email(firstname_email[1], firstname_email[0], new_pswd)

			cur.execute("UPDATE User SET password=%s WHERE username=%s", (new_pswd, user_name))
			mysql.connection.commit()
		except: 
			print "Get or set email query is wrong! \nSet password query is wrong!"
		finally:
			cur.close()

		options = {
			"edit": False,
			"login": True,
			"refill": False
		}
		return render_template("user.html", options=options)
	else:
		return render_template("user_pswd_reset.html")
