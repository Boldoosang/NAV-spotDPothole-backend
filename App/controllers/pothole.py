#Justin Baldeosingh
#SpotDPothole-Backend
#NULLIFY

#POTHOLE CONTROLLERS - Facilitate interactions between the pothole model and the other models/controllers of the application.

#Imports flask modules and json.
from flask import Flask, request, session
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, current_user
import json

#Imports the all of the models and controllers of the application.
from App.models import *
from App.controllers import *

#Retrieves all of the potholes that are in the database and returns their dictionary definitions in an array, in json form, as well as
#an 'OK' http status code (200).
def getPotholeData():
    try:
        #Retrieves all of the potholes from the database.
        potholes = db.session.query(Pothole).all()
        #Gets the dictionary definition of each of the potholes and stores them in an array.
        potholeData = [p.toDict() for p in potholes]
        #Returns the json form of the array, as well as an OK http status (200) code.
        return json.dumps(potholeData), 200
    except:
        return json.dumps({"error": "Invalid pothole details specified."}), 400

#Retrieives and returns data for an individual pothole given the pothole ID.
def getIndividualPotholeData(potholeID):
    try:
        #Retrieves the first pothole, with the specified potholeID, from the database.
        pothole = db.session.query(Pothole).filter_by(potholeID=potholeID).first()
        #If a pothole with the given potholeID is not found, return a 'Not Found' error and status code.
        if not pothole:
            return {"error" : "No pothole data for that ID."}, 404

        #If a pothole with the potholeID is found, get the dictionary definition of the pothole and return the definition in JSON form.
        potholeData = pothole.toDict()
        #Returns the json data for the found pothole and an OK status code (200).
        return json.dumps(potholeData), 200
    #If the potholeID is invalid, return an error and BAD REQUEST status code (400)
    except:
        return json.dumps({"error": "Invalid pothole ID specified."}), 400

#Deletes a pothole given a particular potholeID.
def deletePothole(potholeID):
    try:

        #Finds the pothole corresponding to the input potholeID.
        pothole = db.session.query(Pothole).filter_by(potholeID=potholeID).first()
        #If no pothole is found, return False that it could not be deleted.
        if not pothole:
            return False
        #Otherwise if it is found, delete the pothole, commit the change, and return True that the operation was successful.
        else:
            try:
                db.session.delete(pothole)
                db.session.commit()
                return True
            except:
            #If the deletion operation fails, rollback the database and return False that the pothole could not be deleted.
                db.session.rollback()
                return False
    #If the potholeID is invalid, return an error and BAD REQUEST status code (400)
    except:
        return json.dumps({"error": "Invalid pothole ID specified."}), 400

#Deletes all of the potholes that have expired.
def deleteExpiredPotholes():
    try:
        #Gets all of the expired potholes, that is, gets all of the potholes where the expiry date has passed.
        expiredPotholes = db.session.query(Pothole).filter(datetime.now() >= Pothole.expiryDate).all()
        #Iterates over all of the expired potholes and deletes them.
        for pothole in expiredPotholes:
            deletePothole(pothole.potholeID)
    except:
        print("error deleting expired potholes")
        db.session.rollback()


##################### TEST CONTROLLERS #####################

def getAllPotholes():
    try:
        allReports = db.session.query(Pothole).filter_by().all()
        allReports = [r.toDict() for r in allReports]
        return allReports
    except:
        return []

def nukePotholesInDB():
    try:
        allPotholes = db.session.query(Pothole).all()
        for pothole in allPotholes:
            db.session.delete(pothole)
            db.session.commit()
    except:
        return "Unable to nuke!"