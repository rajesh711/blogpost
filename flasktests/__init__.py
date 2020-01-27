from flask import Flask
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flasktests.config import Config

mongo = PyMongo()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_massage_category = 'info'



def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    mongo.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)


    from flasktests.users.routes import users
    from flasktests.posts.routes import posts
    from flasktests.main.routes import main
    from flasktests.admin.routes import admin
    from flasktests.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(admin)
    app.register_blueprint(errors)
    return app
