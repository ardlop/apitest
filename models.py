import time, hashlib, binascii
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "tbUsers"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)
    email = db.Column(db.String(60))
    password = db.Column(db.String(100))
    timestamp = db.Column(db.String(100))

    def __init__(self, username, email, password):
    	self.username = username
    	self.email = email
    	salt = time.time()
    	dk = hashlib.pbkdf2_hmac('sha256', password, str(salt), 100000)
    	pswd = binascii.hexlify(dk)
    	self.password = pswd
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

