
from flask import Flask, render_template, request, redirect, session
import controllers
import os

from extensions import mysql, mail

app = Flask(__name__, template_folder='views')

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'eecs485group87pa2@gmail.com'
app.config['MAIL_PASSWORD'] = 'group87pa2'
mail.init_app(app)

app.config['MYSQL_USER'] = 'group187'
app.config['MYSQL_PASSWORD'] = 'group187'
app.config['MYSQL_DB'] = 'group187pa4'
app.config['MYSQL_HOST'] = 'localhost'
mysql.init_app(app)

app.secret_key = os.urandom(24)

app.register_blueprint(controllers.album)
app.register_blueprint(controllers.albums)
app.register_blueprint(controllers.pic)
app.register_blueprint(controllers.main)
app.register_blueprint(controllers.user)
app.register_blueprint(controllers.api)

# comment this out using a WSGI like gunicorn
# if you dont, gunicorn will ignore it anyway
if __name__ == '__main__':
    # listen on external IPs
    app.run(host='eecs485-09.eecs.umich.edu', port=5787, debug=True)
