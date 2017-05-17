from flask import Flask, session, request, flash, url_for, redirect, render_template, abort ,g, jsonify 
from models import *
import ConfigParser, time, hashlib, binascii
from flask_sqlalchemy import SQLAlchemy
from socket import gethostname
from flask_login import LoginManager, login_user , logout_user , current_user , login_required
from werkzeug.security import gen_salt
from flask_oauthlib.provider import OAuth1Provider


app = Flask(__name__)

app.debug = True
app.secret_key = 'secret'

config = ConfigParser.ConfigParser()
config.read('app.conf')

connectMYSQL = 'mysql://' + config.get('DBTEST', 'user') + \
':' + config.get('DBTEST', 'password') + '@' + \
config.get('DBTEST', 'host') + '/' + config.get('DBTEST', 'db')
app.config['SQLALCHEMY_DATABASE_URI'] = connectMYSQL
#app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

app.config.update({
	'OAUTH1_PROVIDER_ENFORCE_SSL': False,
	'OAUTH1_PROVIDER_KEY_LENGTH': (10, 100),
})

### oauth1 settings

oauth = OAuth1Provider(app)

def current_user():
	if 'id' in session:
		uid = session['id']
		print uid
		return User.query.get(uid)
	return None

@oauth.clientgetter
def load_client(client_key):
	print 'clientgetter'
	client = Client.query.filter_by(client_key=client_key).first()
	return client


@oauth.grantgetter
def load_request_token(token):
	print 'grantgetter'
	return RequestToken.query.filter_by(token=token).first()


@oauth.grantsetter
def save_request_token(token, request):
	print 'grantsetter'
	if hasattr(oauth, 'realms') and oauth.realms:
					realms = ' '.join(request.realms)
	else:
					realms = None
	grant = RequestToken(
					token=token['oauth_token'],
					secret=token['oauth_token_secret'],
					client=request.client,
					redirect_uri=request.redirect_uri,
					_realms=realms,
	)
	db.session.add(grant)
	db.session.commit()
	return grant


@oauth.verifiergetter
def load_verifier(verifier, token):
	print 'verifiergetter'
	return RequestToken.query.filter_by(
					verifier=verifier, token=token
	).first()


@oauth.verifiersetter
def save_verifier(token, verifier, *args, **kwargs):
	print 'verifiersetter'
	tok = RequestToken.query.filter_by(token=token).first()
	tok.verifier = verifier['oauth_verifier']
	tok.user = current_user()
	db.session.add(tok)
	db.session.commit()
	return tok


@oauth.noncegetter
def load_nonce(client_key, timestamp, nonce, request_token, access_token):
	print 'noncegetter'
	return Nonce.query.filter_by(
					client_key=client_key, timestamp=timestamp, nonce=nonce,
					request_token=request_token, access_token=access_token,
	).first()


@oauth.noncesetter
def save_nonce(client_key, timestamp, nonce, request_token, access_token):
	print 'noncesetter'
	nonce = Nonce(
					client_key=client_key,
					timestamp=timestamp,
					nonce=nonce,
					request_token=request_token,
					access_token=access_token,
	)
	db.session.add(nonce)
	db.session.commit()
	return nonce

@oauth.tokengetter
def load_access_token(client_key, token, *args, **kwargs):
	print 'tokengetter'
	return AccessToken.query.filter_by(
					client_key=client_key, token=token
	).first()


@oauth.tokensetter
def save_access_token(token, request):
	print 'tokensetter'
	tok = AccessToken(
					client=request.client,
					user=request.user,
					token=token['oauth_token'],
					secret=token['oauth_token_secret'],
					_realms=token['oauth_authorized_realms'],
	)
	db.session.add(tok)
	db.session.commit()

@app.route('/oauth/request_token')
@oauth.request_token_handler
def request_token():
	u = current_user()
	print u is None
	print 'request_token_handler'
	return {}


@app.route('/oauth/access_token')
@oauth.access_token_handler
def access_token():
	print 'access_token_handler'
	return {}


@app.route('/oauth/authorize', methods=['GET', 'POST'])
@oauth.authorize_handler
def authorize(*args, **kwargs):
	print 'authorize_handler'
	user = current_user()
	print args
	print kwargs
	#if not user:
	#	print 'not user'
	#	return redirect('/')
	if request.method == 'GET':
		print kwargs
		client_key = kwargs.get('resource_owner_key')
		client = Client.query.filter_by(client_key=client_key).first()
		kwargs['client'] = client
		kwargs['user'] = user
		return render_template('authorize.html', **kwargs)
	confirm = request.form.get('confirm', 'no')
	return confirm == 'yes'



### login settings

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
	return User.query.get(int(id))

@app.before_request
def before_request():
	g.user = current_user

### My views

@app.route('/hello')
@login_required
def hello_world():
	return connectMYSQL

@app.route('/hi')
@oauth.require_oauth()
def holaOauth():
	return "Authenticated via Oauth"


@app.route('/', methods=('GET', 'POST'))
def login():
	if request.method == 'GET':
		return render_template('login.html')
	if request.method == 'POST':
		#username = request.form.get('username')
		#user = User.query.filter_by(username=username).first()
		username = request.form['username']
		password = request.form['password']
		user = User.query.filter_by(username=username).first()
		
		if user is None or user.password != password:
			flash('Username or Password is invalid' , 'error')
			return redirect(url_for('login'))
		
		#if not user:
		#	user = User(username=username, password = password, email='test@test.com')
		#	db.session.add(user)
		#	db.session.commit()
		session['id'] = user.id
		login_user(user)
		flash('Logged in successfully')
	return redirect(request.args.get('next') or url_for('client'))

@app.route('/client')
def client():
	try:
		user = current_user()
		if not user:
			return redirect(url_for('login'))

		client = Client.query.filter_by(user_id = user.id).first()
		if client is None:
			item = Client(
			client_key=gen_salt(40),
			client_secret=gen_salt(50),
			_redirect_uris='http://localhost:8000/authorized',
			user_id=user.id,
			)
			db.session.add(item)
			db.session.commit()
			return jsonify(client_key=item.client_key,
			client_secret=item.client_secret)
		else:
			return jsonify(client_key=client.client_key,
				client_secret=client.client_secret)
	except Exception as e:
		flash(e.message)
		return redirect(url_for('login'))


if __name__ == '__main__':
	db.init_app(app)
	with app.app_context():
		db.create_all()	
	app.run()