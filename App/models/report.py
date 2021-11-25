#Justin Baldeosingh
#SpotDPothole-Backend
#NULLIFY

#REPORT MODEL - Defines the attributes for the report model, and the relationship between the different tables.

#Imports flask modules and datetime.
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#Imports the shared database to be used in defining the model without overwriting the database.
from .sharedDB import db

#Defines the report database table.
class Report(db.Model):
    reportID = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String(500), nullable = False)
    dateReported = db.Column(db.Date, nullable = False, default=datetime.utcnow)

    #Foreign key that references the user table.
    userID = db.Column(db.Integer, db.ForeignKey("user.userID"), nullable = False)
    #Foreign key that references the pothole table.
    potholeID = db.Column(db.Integer, db.ForeignKey("pothole.potholeID"), nullable=False)

    #Declares a relationship with the Vote table, such that all of the votes for a report are deleted when the report is deleted.
    votes = db.relationship('UserReportVote', cascade="all, delete", backref='report')
    #Declares a relationship with the ReportedImage table, such that all of the reportedImages for a report are deleted when the report is deleted.
    reportedImages = db.relationship('ReportedImage', cascade="all, delete", backref='report')
    
    #Prints the details for a particular report record.
    def toDict(self):
        return {
            "reportID" : self.reportID,
            "userID" : self.userID,
            "potholeID" : self.potholeID,
            "dateReported" : self.dateReported.strftime("%Y-%m-%d"),
            "description" : self.description,
            "votes" : [vote.toDict() for vote in self.votes],
            "reportedImages" : [rImage.toDict() for rImage in self.reportedImages],
            "reportedBy" : self.user.firstName + " " + self.user.lastName
        }
