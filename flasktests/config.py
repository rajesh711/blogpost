import os


class Config:
    if not os.environ.get('SECRET_KEY', None):
        print('SECRET_KEY is not defined in environment variable')
        print('exiting app')
        exit(1)
    if not os.environ.get('MONGO_URI', None):
        print('MONGO_URI is not defined in environment variable')
        print('exiting app')
        exit(1)
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MONGO_URI = os.environ.get('MONGO_URI')
