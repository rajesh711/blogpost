import os
from flask import Flask
from flask_login import login_user, current_user, logout_user, LoginManager
from flasktests.forms import RegistrationForm, LoginForm
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt

app = Flask(__name__)
# app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
# app.config[""] = "mongodb://localhost:27017/blogdb"

# mongo = PyMongo(app,uri="mongodb://localhost:27017/blogdb")
mongo = PyMongo(app,os.environ.get('MONGO_URI'))

# # connect to another MongoDB database on the same host
# mongo1 = PyMongo(app,uri="mongodb://localhost:27017/blogdb1")
#
# # connect to another MongoDB server altogether
# mongo2 = PyMongo(app,uri="mongodb://localhost:27017/blogdb2")

# mongo = PyMongo(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_massage_category = 'info'


from flasktests import routes