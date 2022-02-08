#Justin Baldeosingh
#SpotDPothole-Backend
#NULLIFY

#Import Modules
from flask import Flask, request, session
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta 
import os

#Imports the models and views of the application.
from App.models import *
from App.views import (potholeViews, userViews, reportedImageViews, reportViews, userReportVoteViews, dashboardViews)
views = [potholeViews, userViews, reportedImageViews, reportViews, userReportVoteViews, dashboardViews]

#Registers the different view blueprints for the different API endpoints.
def addViews(app, views):
    for view in views:
        app.register_blueprint(view)


#Creates the manager for the application, for the JSON web tokens using in authentication.
jwt = JWTManager()

#Loads the configuration into the application from either a config file, or using environment variables.
def loadConfig(app, config):
    #Attempts to configure the application from a configuration file.
    try:
        app.config.from_object('App.config.development')
    except:
    #If no configuration file is present, use the environment variables of the host to configure the application.
        print("Config file not present. Using environment variables.")
        DBURI = os.environ.get('DBURI')
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') if os.environ.get('SECRET_KEY') != None else "DEFAULT_SECRET_KEY"
        app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days = 30)
        app.config['DEBUG'] = os.environ.get('DEBUG')
        app.config['ENV'] = os.environ.get('ENV')
        SQLITEDB = os.environ.get("SQLITEDB", default="False") 

        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///spotDPothole.db" if SQLITEDB in ["True", "true", "TRUE"] else os.environ.get('DBURI')

    
    #Used to initialize db for fixture
    for key,value in config.items():
        app.config[key] = config[key]


def init_db(app):
    db.init_app(app)
    db.create_all(app=app)
    db.session.commit()

#Creates the application, loads the configuration, adds the views, initializes the database, creates the JWT manager, and returns the application context.
def create_app(config={}):
    app = Flask(__name__)
    CORS(app)
    loadConfig(app, config)
    addViews(app, views)
    db.init_app(app)
    app.app_context().push()
    jwt.init_app(app)
    return app

#Allows for a user object to be returned once they have been identified within the database.
def identity(payload):
  return db.session.query(User).get(payload['identity'])

#Determines whether the credentials for a user is correct and returns the user object associated with those credentials.
def authenticate(email, password):
    #Finds the user with the corresponding email.
    user = User.filter_by(email=email).first()
    #If the user exists and the password is correct, the user is verified and the user object is returned.
    if user and user.checkPassword(password):
        return user

# Flask Boilerplate for loading a user's context.
# Register a callback function that loades a user from your database whenever
# a protected route is accessed. This should return any python object on a
# successful lookup, or None if the lookup failed for any reason (for example
# if the user has been deleted from the database).

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(email=identity).one_or_none()


if __name__ == "__main__":
    app = create_app()
    init_db(app)


