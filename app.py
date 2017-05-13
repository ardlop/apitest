from flask import Flask
from models import db, User
import ConfigParser

app = Flask(__name__)

onfig = ConfigParser.ConfigParser()
config.read('config.py')

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://' + config.get('DB', 'user') + \
':' + config.get('DB', 'password') + '@' + \
config.get('DB', 'host') + '/' + config.get('DB', 'db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)


@app.route('/')
def hello_world():
    return 'Hello from Flask!'

'''
if __name__ == '__main__':
    db.create_all()
    app.run()
'''
