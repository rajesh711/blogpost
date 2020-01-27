from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin
from bson.objectid import ObjectId
from flasktests import login_manager, bcrypt, mongo


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


class User(UserMixin):
    def __init__(self, username, email, password, image="default.jpg", authenticated=True, active=True,
                 anonymous=False, _id=None):
        self.username = username
        self.email = email
        self.password = password
        self.image = image
        self.authenticated = authenticated
        self.active = active
        self.anonymous = anonymous
        self._id = _id

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image}')"

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return self.anonymous

    def get_id(self):
        return str(self._id)

    @classmethod
    def get_by_username(cls, username):
        data = mongo.db.User.find_one({"username": username})
        if data is not None:
            return cls(**data)
        return None

    @classmethod
    def get_by_email(cls, email):
        data = mongo.db.User.find_one({"email": email})
        if data is not None:
            return cls(**data)
        return None

    @classmethod
    def get_by_id(cls, str_mongo_id):
        data = mongo.db.User.find_one({"_id": ObjectId(str_mongo_id)})
        if data is not None:
            return cls(**data)
        return None

    @classmethod
    def get_all(cls, query={}):
        return mongo.db.User.find(query)

    @staticmethod
    def login_valid(email, password):
        verify_user = User.get_by_email(email)
        if verify_user is not None:
            return bcrypt.check_password_hash(verify_user.password, password)
        return False

    @classmethod
    def register(cls, username, email, password, image="default.jpg", authenticated=True, active=True, anonymous=False):
        user = cls.get_by_email(email)
        if user is None:
            new_user = cls(username, email, password, image=image, authenticated=authenticated, active=active,
                           anonymous=anonymous)
            new_user.save_to_mongo()
            return True
        else:
            return False

    @classmethod
    def update_by_user_id(cls, str_mongo_id, new_val):
        print(new_val)
        data = mongo.db.User.update_one({"_id": ObjectId(str_mongo_id)}, {"$set": new_val})
        if data:
            return True
        else:
            return False

    def json(self):
        return {
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "image": self.image,
            "authenticated": self.authenticated,
            "active": self.active,
            "anonymous": self.anonymous
        }

    def save_to_mongo(self):
        mongo.db.User.insert(self.json())


class Document(dict):
    """
    A simple model that wraps mongodb document
    """
    __getattr__ = dict.get
    __delattr__ = dict.__delitem__
    __setattr__ = dict.__setitem__

    def save(self):
        print('self._id ', self._id)
        if not self._id:
            self.pop('_id', None)
            self.collection.insert(self)
        else:
            self.collection.update(
                {"_id": ObjectId(self._id)}, self)

    def reload(self):
        if self._id:
            self.update(self.collection \
                        .find_one({"_id": ObjectId(self._id)}))

    def remove(self):
        if self._id:
            self.collection.remove({"_id": ObjectId(self._id)})
            self.clear()

    @classmethod
    def find(cls, query={}):
        return cls.collection.find(query)

    @classmethod
    def find_one(cls, query={}):
        return cls.collection.find_one(query)

    @classmethod
    def get_by_id(cls, str_mongo_id):
        return cls.collection.find_one({"_id": ObjectId(str_mongo_id)})

    @classmethod
    def delete_by_id(cls, str_mongo_id):
        data = cls.collection.delete_one({"_id": ObjectId(str_mongo_id)})
        if data:
            return True
        else:
            return False

    @classmethod
    def update_by_id(cls, str_mongo_id, new_val):
        data = cls.collection.update_one({"_id": ObjectId(str_mongo_id)}, {"$set": new_val})
        if data:
            return True
        else:
            return False


class Post(Document):
    collection = mongo.db.Post

    def __init__(self, title, content, author, _id=None):
        self.title = title
        self.content = content
        self.author = author
        self.date_posted = datetime.utcnow()
        self._id = _id

    def get_id(self):
        return str(self._id)

    def __repr__(self):
        return f"Post('_id : {self._id}  Title : {self.title}   Content : {self.content} ')"
