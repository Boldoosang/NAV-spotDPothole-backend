#Justin Baldeosingh
#SpotDPothole-Backend
#NULLIFY

#Import Modules
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

#Import models and controllers
from App.models import *
from App.controllers import *

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

