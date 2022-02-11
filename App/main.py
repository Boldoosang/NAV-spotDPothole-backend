#Justin Baldeosingh
#SpotDPothole-Backend
#NULLIFY

#Import Modules
from flask import Flask, request, url_for, session
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from datetime import timedelta 
import os

#Imports the models and views of the application.
from App.models import *
from App.views import *
from App.views import (potholeViews, userViews, reportedImageViews, reportViews, userReportVoteViews, dashboardViews)
views = [potholeViews, userViews, reportedImageViews, reportViews, userReportVoteViews, dashboardViews]
from authlib.integrations.flask_client import OAuth

#Registers the different view blueprints for the different API endpoints.
def addViews(app, views):
    for view in views:
        app.register_blueprint(view)


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
        app.config['SESSION_COOKIE_NAME'] = 'google-login-session'
        app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
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
    oauth.init_app(app)
    return app

if __name__ == "__main__":
    app = create_app()
    init_db(app)

