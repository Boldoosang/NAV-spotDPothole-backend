#Justin Baldeosingh
#SpotDPothole-Backend
#NULLIFY

#POTHOLE CONTROLLERS - Facilitate interactions between the pothole model and the other models/controllers of the application.

#Imports json.
import json

#Imports the all of the required models and controllers.
from App.models import *
from App.controllers import *
from App.controllers.reportedImage import deleteAllPotholeImagesFromStorage, deleteAllReportImagesFromStorage, deleteImageFromStorage

#Retrieves all of the potholes that are in the database and returns their dictionary definitions in an array, in json form, as well as
#an 'OK' http status code (200).
def getPotholeData():
    #Attempts to get and return all of the potholes in the database.
    try:
        #Retrieves all of the potholes from the database.
        potholes = db.session.query(Pothole).all()
        #Gets the dictionary definition of each of the potholes and stores them in an array.
        potholeData = [p.toDict() for p in potholes]
        #Returns the json form of the array, as well as an OK http status (200) code.
        return json.dumps(potholeData), 200
    except:
    #If an error was encountered in getting the pothole data, rollback the query (querying invalid datatype crashes POSTGRES database ONLY)
        db.session.rollback()
        return json.dumps({"error": "Invalid pothole details specified."}), 400


#Retrieves all of the user's potholes that are in the database and returns their dictionary definitions in an array, in json form, as well as
#an 'OK' http status code (200).
def getUserPotholeData(user):
    #Attempts to get and return all of the user's potholes in the database.
    try:
        #Retrieves all of the potholes from the database.
        potholes = db.session.query(Pothole).filter_by().all()

        potholeData = []

        for pothole in potholes:
            potholeData += [pothole.toDict() for report in pothole.reports if user.userID == report.userID]

        return json.dumps(potholeData), 200
    except:
    #If an error was encountered in getting the pothole data, rollback the query (querying invalid datatype crashes POSTGRES database ONLY)
        db.session.rollback()
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
    #If the potholeID is invalid, return an error and BAD REQUEST status code (400) and rollback the database.
    except:
        db.session.rollback()
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
                deleteAllPotholeImagesFromStorage(pothole.potholeID)
                db.session.delete(pothole)
                db.session.commit()
                return True
            except:
            #If the deletion operation fails, rollback the database and return False that the pothole could not be deleted.
                db.session.rollback()
                return False
    #If the potholeID is invalid, return an error and BAD REQUEST status code (400) and rollback the database.
    except:
        db.session.rollback()
        return json.dumps({"error": "Invalid pothole ID specified."}), 400

#Deletes all of the potholes that have expired.
def deleteExpiredPotholes():
    #Attempts to delete all of the expired potholes.
    try:
        #Gets all of the expired potholes, that is, gets all of the potholes where the expiry date has passed.
        expiredPotholes = db.session.query(Pothole).filter(datetime.now() >= Pothole.expiryDate).all()
        #Iterates over all of the expired potholes and deletes them.
        for pothole in expiredPotholes:
            deleteAllPotholeImagesFromStorage(pothole.potholeID)
            deletePothole(pothole.potholeID)
    except:
    #If deleting the expired pothoels result in an error, print a message and rollback the transaction.
        print("error deleting expired potholes")
        db.session.rollback()


##################### TEST CONTROLLERS #####################
#Gets all of the potholes within the database and returns it in an array.
def getAllPotholes():
    #Attempts to get all of the potholes in the database.
    try:
        allReports = db.session.query(Pothole).filter_by().all()
        allReports = [r.toDict() for r in allReports]
        return allReports
    except:
    #If the query fails, rollback and return an empty array.
        db.session.rollback()
        return []

#Removes all potholes, reports, and reported images. Cascade deletion enforces that reports and reported images are deleted.
def nukePotholesInDB():
    #Attempts to delete all of the potholes in the database.
    try:
        #Gets all of the potholes in the database.
        allPotholes = db.session.query(Pothole).all()
        #Individual deletes each of all of the potholes and commits the transaction.
        for pothole in allPotholes:
            deleteAllPotholeImagesFromStorage(pothole.potholeID)
            db.session.delete(pothole)
            db.session.commit()
            
    except:
    #If an error is encountered, rollback the last delete and return an error.
        db.session.rollback()
        return "Unable to nuke!"