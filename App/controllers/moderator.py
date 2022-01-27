#Justin Baldeosingh
#SpotDPothole-Backend
#NULLIFY

#POTHOLE CONTROLLERS - Facilitate interactions between the pothole model and the other models/controllers of the application.

#Imports json.
import json

#Imports the all of the required models and controllers.
from App.models import *
from App.controllers import *

def moderatorDeleteReport(user, reportID):
    try:
        if user.moderator:
            try:
                foundReport = db.session.query(Report).filter_by(reportID = reportID).first()
                db.session.delete(foundReport)
                db.session.commit()
                return {"message" : "Report successfully deleted!"}, 200
            except:
                db.session.rollback()
                return {"error" : "Unable to delete report! Ensure that it exists."}, 404
        else:
            return {"error" : "You do not have permission to delete this report."}, 401

    except:
        db.session.rollback()
        return json.dumps({"error": "An unknown error has occurred!"}), 500

def moderatorBanUser(user, userDetails):
    email = ""
    if "email" in userDetails:
        email = userDetails["email"]
    else:
        return {"error" : "No user email was specified."}, 400
    
    try:
        if user.moderator:
            try:
                foundUser = db.session.query(User).filter_by(email = email).first()
                foundUser.banned = True
                db.session.add(foundUser)
                db.session.commit()
                return {"message" : "User successfully banned!"}, 200
            except:
                db.session.rollback()
                return {"error" : "Unable to ban user! Ensure that their account exists."}, 404
        else:
            return {"error" : "You do not have permission to ban users."}, 401

    except:
        db.session.rollback()
        return json.dumps({"error": "An unknown error has occurred!"}), 500


def moderatorUnbanUser(user, userDetails):
    email = ""
    if "email" in userDetails:
        email = userDetails["email"]
    else:
        return {"error" : "No user email was specified."}, 400
        
    try:
        if user.moderator:
            try:
                foundUser = db.session.query(User).filter_by(email = email).first()
                foundUser.banned = False
                db.session.add(foundUser)
                db.session.commit()
                return {"message" : "User successfully unbanned!"}, 200
            except:
                db.session.rollback()
                return {"error" : "Unable to unban user! Ensure that their account exists."}, 404
        else:
            return {"error" : "You do not have permission to unban users."}, 401

    except:
        db.session.rollback()
        return json.dumps({"error": "An unknown error has occurred!"}), 500