from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SECRET_KEY'] = 'adddb114244c11c9'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['LOGIN_DISABLED'] = False
app.config['TESTING'] = False


db = SQLAlchemy(app)
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)

from web_shop import routes
