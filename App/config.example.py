#Sample Config
#Rename to config.py
from datetime import timedelta 

class development:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///spotDPothole.db'
    SECRET_KEY = ""
    JWTDELTADAYS = 14
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days = 30)
    ENV = 'development'
    SQLITEDB = True
    SECURITY_PASSWORD_SALT = ""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PROPAGATE_EXCEPTIONS = True
    UPLOAD_FOLDER = "App/uploads"
    MAX_CONTENT_LENGTH = 15 * 1000 * 1000
    JWT_SECRET_KEY = ""
    GOOGLE_CLIENT_ID = ""
    GOOGLE_CLIENT_SECRET = ""
    MAIL_SERVER = ""
    MAIL_USERNAME = ""
    MAIL_PASSWORD = ""
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False

class production:
    SQLALCHEMY_DATABASE_URI = ''
    SECRET_KEY = ""
    JWTDELTADAYS = 14
    ENV = 'development'
    SECURITY_PASSWORD_SALT = ""
    SQLITEDB = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PROPAGATE_EXCEPTIONS = True
    UPLOAD_FOLDER = "App/uploads"
    MAX_CONTENT_LENGTH = 15 * 1000 * 1000
    JWT_SECRET_KEY = ""
    GOOGLE_CLIENT_ID = ""
    GOOGLE_CLIENT_SECRET = ""
    MAIL_SERVER = ""
    MAIL_USERNAME = ""
    MAIL_PASSWORD = ""
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False