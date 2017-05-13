from flask import Flask
from models import db, User
import ConfigParser
from flask_sqlalchemy import SQLAlchemy
from socket import gethostname


app = Flask(__name__)
'''
config = ConfigParser.ConfigParser()
config.read('config.py')

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
        username = config.get('DB', 'user'),
        password = config.get('DB', 'password') ,
        hostname =  config.get('DB', 'host'),
        databasename =  config.get('DB', 'db'),)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
'''
'''
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://' + config.get('DB', 'user') + \
':' + config.get('DB', 'password') + '@' + \
config.get('DB', 'host') + '/' + config.get('DB', 'db')
'''

app.config["DEBUG"] = True
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
        username="ardlop",
        password="Elcoco.com",
        hostname="ardlop.mysql.pythonanywhere-services.com",
        databasename="ardlop$apiDB",)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

@app.route('/')
def hello_world():
    #return SQLALCHEMY_DATABASE_URI;
    return 'Hello from Flask! UPDATED!!'


if __name__ == '__main__':
    db.create_all()
    if 'liveconsole' not in gethostname():
        app.run()

