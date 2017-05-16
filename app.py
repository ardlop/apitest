from flask import Flask, session, request, flash, url_for, redirect, render_template, abort ,g
from models import db, User
import ConfigParser, hashlib, binascii, time
from flask_sqlalchemy import SQLAlchemy
from socket import gethostname
from flask_login import LoginManager, login_user , logout_user , current_user , login_required

app = Flask(__name__)

app.debug = True
app.secret_key = 'secret'

config = ConfigParser.ConfigParser()
config.read('app.conf')

connectMYSQL = 'mysql://' + config.get('DB', 'user') + \
':' + config.get('DB', 'password') + '@' + \
config.get('DB', 'host') + '/' + config.get('DB', 'db')
app.config['SQLALCHEMY_DATABASE_URI'] = connectMYSQL
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'templates/login'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

@app.route('/')
def hello_world():
    return connectMYSQL

@app.route('/login', methods=['GET','POST'])
def login():
	if request.method == 'GET':
		return render_template('login.html')
	username = request.form['username']
	password = request.form['password']
	registered_user = User.query.filter_by(username=username).first()

	if registered_user is None:
		flash('Username or Password is invalid' , 'error')
		return redirect(url_for('login'))

	salt = registered_user.timestamp
	print salt
	dk = hashlib.pbkdf2_hmac('sha256', password, 'SAEAPP', 100000)
	pswd = binascii.hexlify(dk)
	print registered_user
	print registered_user.password == pswd
	print registered_user.password
	print pswd

	login_user(registered_user)
	flash('Logged in successfully')
	return redirect(request.args.get('next') or url_for('hello_world'))
	#return redirect(request.args.get('next') or url_for('index'))


if __name__ == '__main__':
	db.init_app(app)
	with app.app_context():
		db.create_all()	
		salt = time.time()
		dk = hashlib.pbkdf2_hmac('sha256', 'test', 'SAEAPP', 100000)
		pswd = binascii.hexlify(dk)

		'''
		user = User(
		username = 'test',
		email='test@test.com',
		password = pswd
		)

		db.session.add(user)
		db.session.commit()
		'''
		#>>> dk = hashlib.pbkdf2_hmac('sha256', b'test', b'SAEAPP', 100000)
	app.run()
    #db.create_all()
    #if 'liveconsole' not in gethostname():
    #    app.run()

