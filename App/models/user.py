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
    googleID = db.Column(db.String(32), unique = True, nullable = True)
    email = db.Column(db.String(64), unique = True)
    firstName = db.Column(db.String(64), nullable = False)
    lastName = db.Column(db.String(64), nullable = False)
    picture = db.Column(db.String(300), nullable = True)
    banned = db.Column(db.Boolean, nullable = False, default=0, server_default="0")

    #Declares a relationship with the Report table, such that all of the reports for a user are deleted when the user is deleted.
    reports = db.relationship('Report', cascade="all, delete", backref='user')
    #Declares a relationship with the Vote table, such that all of the votes for a user are deleted when the user is deleted.
    votes = db.relationship('UserReportVote', cascade="all, delete", backref='voter')

    #Defines the constructor used to initialize a new user instance/object.
    def __init__(self, googleID, email, firstName, lastName, banned, picture):
        self.email = email
        self.firstName = firstName
        self.lastName = lastName
        self.googleID = googleID
        self.banned = banned
        self.picture = picture

    #Prints the details for a particular user record.
    def toDict(self):
        return {
            "userID" : self.userID,
            "email" : self.email,
            "firstName" : bleach.clean(self.firstName),
            "lastName" : bleach.clean(self.lastName),
        }
    