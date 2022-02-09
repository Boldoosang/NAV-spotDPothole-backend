#Justin Baldeosingh
#SpotDPothole-Backend
#NULLIFY

#USER MODEL - Defines the attributes for the user model, and the relationship between the different tables.

#Imports flask modules and werkzeug security modules.
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import bleach

#Imports the shared database to be used in defining the model without overwriting the database.
from .sharedDB import db

#Defines the User database table.
class User(db.Model):
    userID = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(64), unique = True)
    firstName = db.Column(db.String(64), nullable = False)
    lastName = db.Column(db.String(64), nullable = False)
    password = db.Column(db.String(256), nullable = False)
    banned = db.Column(db.Boolean, nullable = False, default=0, server_default="0")

    #Declares a relationship with the Report table, such that all of the reports for a user are deleted when the user is deleted.
    reports = db.relationship('Report', cascade="all, delete", backref='user')
    #Declares a relationship with the Vote table, such that all of the votes for a user are deleted when the user is deleted.
    votes = db.relationship('UserReportVote', cascade="all, delete", backref='voter')

    #Defines the constructor used to initialize a new user instance/object.
    def __init__(self, email, firstName, lastName, password):
        self.email = email
        self.firstName = firstName
        self.lastName = lastName
        self.setPassword(password)

    #Sets the password of a user by hashing and storing the input password.
    def setPassword(self, password):
        self.password = generate_password_hash(password, method='sha256')
    
    #Checks the hashed input password to the stored hashed user password to determine if the user can be verified. Returns true if matches.
    def checkPassword(self, password):
        return check_password_hash(self.password, password)

    #Prints the details for a particular user record.
    def toDict(self):
        return {
            "userID" : self.userID,
            "email" : self.email,
            "firstName" : bleach.clean(self.firstName),
            "lastName" : bleach.clean(self.lastName),
            "password" : self.password
        }
    