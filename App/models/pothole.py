#Justin Baldeosingh
#SpotDPothole-Backend
#NULLIFY

#POTHOLE MODEL - Defines the attributes for the pothole model, and the relationship between the different tables.

#Imports flask modules and datetime.
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

#Imports the shared database to be used in defining the model without overwriting the database.
from .sharedDB import db

#Defines the pothole database table.
class Pothole(db.Model):
    potholeID = db.Column(db.Integer, primary_key = True)
    longitude = db.Column(db.Float, nullable = False)
    latitude = db.Column(db.Float, nullable = False)
    expiryDate = db.Column(db.Date, nullable = False)

    #Declares a relationship with the Report table, such that all of the reports for a pothole are deleted when the pothole is deleted.
    reports = db.relationship('Report', backref=db.backref("reports", uselist=False), cascade="all, delete")

    #Prints the details for a particular pothole record.
    def toDict(self):
        return {
            "potholeID" : self.potholeID,
            "longitude" : self.longitude,
            "latitude" : self.latitude,
            "numReports" : len(self.reports),
            "expiryDate" : self.expiryDate.strftime("%Y-%m-%d")
        }
    