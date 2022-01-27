#Justin Baldeosingh
#SpotDPothole-Backend
#NULLIFY

#Import Modules
from collections import UserString
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

#Import models and controllers
from App.models import *
from App.controllers import *
from App.controllers.pothole import deleteExpiredPotholes, nukePotholesInDB

#Imports the main application object 
from App.main import *

#Creates app and initializes database
app = create_app()
init_db(app)

#Initializes the manager for the application and the database migrator.
manager = Manager(app)
migrate = Migrate(app, db)

#Sets the migration command for migrating the database.
manager.add_command('db', MigrateCommand)

#Initializes the database via the 'python3 manage.py initDB' command.
#Creates the database for the application and prints a message once the initialization is complete.
@manager.command
def initDB():
    db.create_all(app=app)
    print('Database Initialized!')

#Defines code that should be run at startup of the server.
def bootstrapServer():
    #Deletes expired potholes.
    deleteExpiredPotholes()

#Enables the deletion of a pothole by potholeID.
@manager.command
def removePothole(potholeID):
    try:
        deletePothole(potholeID=potholeID)
        print("Successfully deleted pothole!")
    except:
        db.session.rollback()
        print("Unable to delete pothole!")


#Enables the deletion of a pothole by potholeID.
@manager.command
def removeReport(reportID):
    try:
        deletePotholeReport(reportID=reportID)
        print("Successfully deleted report!")
    except:
        db.session.rollback()
        print("Unable to delete report!")


#Enables the removal of all potholes in the system.
@manager.command
def nukePotholes():
    try:
        nukePotholesInDB()
    except:
        db.session.rollback()
        print("Unable to nuke potholes!")

@manager.command
def addModerator(email):
    try:
        foundUser = db.session.query(User).filter_by(email=email).first()
        if(foundUser):
            try:
                foundUser.moderator = True
                db.session.add(foundUser)
                db.session.commit()
            except:
                print("Unable to add moderator!")
        else:
            print("No user found with that email!")
    except:
        db.session.rollback()
        print("Unable to add moderator!")

@manager.command
def removeModerator(email):
    try:
        foundUser = db.session.query(User).filter_by(email=email).first()
        if(foundUser):
            try:
                foundUser.moderator = False
                db.session.add(foundUser)
                db.session.commit()
            except:
                print("Unable to remove moderator!")
        else:
            print("No user found with that email!")
    except:
        db.session.rollback()
        print("Unable to remove moderator!")

@manager.command
def banUser(email):
    try:
        foundUser = db.session.query(User).filter_by(email=email).first()
        if(foundUser):
            try:
                foundUser.banned = True
                db.session.add(foundUser)
                db.session.commit()
            except:
                print("Unable to ban user!")
        else:
            print("No user found with that email!")
    except:
        db.session.rollback()
        print("Unable to ban user!")

@manager.command
def unbanUser(email):
    try:
        foundUser = db.session.query(User).filter_by(email=email).first()
        if(foundUser):
            try:
                foundUser.banned = False
                db.session.add(foundUser)
                db.session.commit()
            except:
                print("Unable to ban user!")
        else:
            print("No user found with that email!")
    except:
        db.session.rollback()
        print("Unable to ban user!")


#Allows the flask application to be served via the 'python3 manage.py serve' command.
#Prints the mode in which the application is running, and also serves the application.
@manager.command
def serve():
    print('Application running in ' + app.config['ENV'] + ' mode!')
    #Carries out startup tasks for application server.
    bootstrapServer()
    app.run(host='0.0.0.0', port = 8080, debug = app.config['ENV'] == 'development')


#If the application is run via 'manage.py', facilitate manager arguments.
if __name__ == "__main__":
    manager.run()

