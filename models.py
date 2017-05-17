import time, hashlib, binascii
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
	__tablename__ = "tbUsers"
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(40), unique=True)
	email = db.Column(db.String(60))
	password = db.Column(db.String(64))
	timestamp = db.Column(db.String(100))

	def __init__(self, username, email, password):
		self.username = username
		self.email = email
		salt = time.time()
		#dk = hashlib.pbkdf2_hmac('sha256', password, str(salt), 100000)
		#pswd = binascii.hexlify(dk)
		self.password = password
		self.timestamp = salt

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return unicode(self.id)

	def __repr__(self):
		return '<User %r>' % (self.username)

class Client(db.Model):
    client_key = db.Column(db.String(40), primary_key=True)
    client_secret = db.Column(db.String(55), index=True, nullable=False)

    # creator of the client
    user_id = db.Column(db.ForeignKey('tbUsers.id'))
    user = db.relationship('User')
    _realms = db.Column(db.Text)
    _redirect_uris = db.Column(db.Text)

    @property
    def redirect_uris(self):
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def default_realms(self):
        if self._realms:
            return self._realms.split()
        return []


class RequestToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('tbUsers.id', ondelete='CASCADE')
    )
    user = db.relationship('User')

    client_key = db.Column(
        db.String(40), db.ForeignKey('client.client_key'),
        nullable=False,
    )
    client = db.relationship('Client')

    token = db.Column(db.String(255), index=True, unique=True)
    secret = db.Column(db.String(255), nullable=False)

    verifier = db.Column(db.String(255))

    redirect_uri = db.Column(db.Text)
    _realms = db.Column(db.Text)

    @property
    def realms(self):
        if self._realms:
            return self._realms.split()
        return []


class Nonce(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    timestamp = db.Column(db.Integer)
    nonce = db.Column(db.String(40))
    client_key = db.Column(
        db.String(40), db.ForeignKey('client.client_key'),
        nullable=False,
    )
    client = db.relationship('Client')
    request_token = db.Column(db.String(50))
    access_token = db.Column(db.String(50))



class AccessToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_key = db.Column(
        db.String(40), db.ForeignKey('client.client_key'),
        nullable=False,
    )
    client = db.relationship('Client')

    user_id = db.Column(
        db.Integer, db.ForeignKey('tbUsers.id'),
    )
    user = db.relationship('User')

    token = db.Column(db.String(255))
    secret = db.Column(db.String(255))

    _realms = db.Column(db.Text)

    @property
    def realms(self):
        if self._realms:
            return self._realms.split()
        return []
