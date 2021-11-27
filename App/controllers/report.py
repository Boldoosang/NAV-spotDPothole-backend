#Justin Baldeosingh
#SpotDPothole-Backend
#NULLIFY

#REPORT CONTROLLERS - Facilitate interactions between the report model and the other models/controllers of the application.

#CONSTANTS
#Specifies a distance threshold, in meters, that will be used to classify pothole reports to the same pothole, within this proximity.
DISTANCE_THRESHOLD = 20
#Specifies the number of days that should be added to the expiry date of a pothole, before they are deleted.
EXPIRY_DATE_REFRESH = 30
#Specifies the number of days that a pothole record should be initialized with, before they are deleted.
EXPIRY_DATE_PRIMARY = 60

#Imports flask modules, geopy, datetime and json.
from flask import Flask, request, session
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, current_user
from geopy import distance
from datetime import datetime, timedelta
import json, requests
from App.controllers.pothole import deletePothole

#Imports the all of the models and controllers of the application.
from App.models import *
from App.controllers import *

#Referenced from StackOverflow
#https://stackoverflow.com/questions/10543940/check-if-a-url-to-an-image-is-up-and-exists-in-python
#Given a URL, determines if the URL points to an image.
def is_url_image(image_url):
    #Sets the expected image types.
    image_formats = ("image/png", "image/jpeg", "image/jpg")
    #Attempts to send a GET request to the URL.
    try:
        r = requests.get(image_url)
    #If the request fails, the URL would be invalid; return false.
    except:
        return False
    #If the content-type in the headers of the response contains a matching image format, return true.
    if r.headers["content-type"] in image_formats:
        return True
    #Otherwise, return false.
    return False

#Returns a json dump of all of the reports in the database.
def getReportData():
    #Gets all of the reports in the database, gets the dictionary definitions, and returns them all in an array.
    #Also returns a 'OK' http status code (200)
    reports = db.session.query(Report).all()
    reportData = [r.toDict() for r in reports]
    return json.dumps(reportData), 200

#Given the latitude and logitude for a report, finds the closest pothole within a threshold distance specified by DISTANCE_THRESHOLD
def findClosestPothole(latitude, longitude):
    #Initializes the finalPothole to None; there is no selected pothole that is close enough.
    finalPothole = None
    #Creates a tuple using the latitude and longitude reported.
    newPotholeCoords = (latitude, longitude)
    
    #Sets the smallest distance to the nearest pothole to the distance threshold value.
    smallestDistance = DISTANCE_THRESHOLD

    #Gets all of the potholes in the database.
    potholeQuery = db.session.query(Pothole).all()
    #Iterates over all of the potholes in the database and calculates the distance between the pothole and the report location.
    for pothole in potholeQuery:
        centerPotholeCoords = (pothole.latitude, pothole.longitude)
        distanceBetweenPotholes = distance.distance(centerPotholeCoords, newPotholeCoords) * 1000

        #If the distance between the current pothole is less than the smallest distance, set the finalPothole to match the current pothole.
        #This effectively finds the nearest pothole, within the distance threshold, that the report can be matched to.
        if distanceBetweenPotholes < smallestDistance:
            
            finalPothole = pothole

    #Returns the final pothole to be used for the report.
    return finalPothole

#Validates a report of a user via the standard interface before adding it to the database.
def reportPotholeStandard(user, reportDetails):
    #Initializes the finalPothole to be added to None.
    finalPothole = None

    #Determines if the reportDetails contains all of the neccesary fields for processing of the report.
    if "longitude" in reportDetails and "latitude" in reportDetails and "description" in reportDetails:
        #If the coordinates reported are within the bounds for Trinidad and Tobago, process the report.
        if -61.965556 < reportDetails["longitude"] < -60.469077 and 10.028088 < reportDetails["latitude"] < 11.370345:
            #Finds the closest pothole to the coordinates.
            finalPothole = findClosestPothole(reportDetails["latitude"], reportDetails["longitude"])

            #If there does not exist an existing pothole that the report can be mapped to, create a new pothole at the report location.
            if not finalPothole:
                #Attempts to create a pothole record using the report details.
                try:
                    #Creates the report using the report details, adds the report to the database, and commits the changes.
                    newPothole = Pothole(longitude=reportDetails["longitude"], latitude=reportDetails["latitude"], expiryDate=datetime.now() + timedelta(days=EXPIRY_DATE_PRIMARY))
                    db.session.add(newPothole)
                    db.session.commit()

                    #Sets the selected finalPothole to this new pothole object.
                    finalPothole = newPothole
                except:
                #Otherwise, if a pothole cannot be created, rollback the database and return an error with 'INTERNAL SERVER ERROR' status code.
                    db.session.rollback()
                    return {"error": "Error adding pothole to database!"}, 500
            #Otherwise, if there exists an existing pothole that the report can be mapped to, create a report for that location.
            else:
                #Determines if a report has already been submitted by the user for this pothole.
                alreadySubmitted = db.session.query(Report).filter_by(userID=user.userID, potholeID=finalPothole.potholeID).first()
                #If a report has already been submitted, a resubmission will reset the expiry date of the pothole.
                if alreadySubmitted:
                    #Updates the expiry date of the pothole by adding a constant number of days to the expiry date.
                    try:
                        #Updates expiry date, adds and commits changes to database. Returns a success message and a 'CREATED' http status code (201).
                        finalPothole.expiryDate = datetime.now() + timedelta(days=EXPIRY_DATE_REFRESH)
                        db.session.add(finalPothole)
                        db.session.commit()
                        return {"message" : "Expiry date of pothole has been reset!"}, 201
                    except:
                    #Otherwise, the pothole could not be updated. Rollback the database and return an error with a 'INTERNAL SERVER ERROR' https tatus code (500).
                        db.session.rollback()
                        return {"error": "Unable to update expiry date!"}, 500
            #Attempts to create a report for the pothole.
            try:
                #Creates a new report for the finalPothole using the description.
                newReport = Report(userID = user.userID, potholeID=finalPothole.potholeID, description=reportDetails["description"])
                #Adds and commits the new report to the database.
                db.session.add(newReport)
                db.session.commit()

                #If there are images in the reportDetails, add the images to the report.
                if "images" in reportDetails:
                    #Iterates over the images within the images field of the reportDetails and adds them to the reportedImage database.
                    for imageURL in reportDetails["images"]:
                        
                        #Determines if the URL is valid and leads to an image.
                        if is_url_image(imageURL):

                            print(imageURL)
                            #If valid, add the imageURL to the reportedImage database for the reportID.
                            try:
                                #Creates image record using report details, adds to database, and commits changes.
                                reportImage = ReportedImage(reportID=newReport.reportID, imageURL=imageURL)
                                db.session.add(reportImage)
                                db.session.commit()
                            except:
                            #Otherwise, rollback the changes for the database and print an appropriate error.
                                db.session.rollback()
                                print("Unable to add this image to database.")

                #Once a new report has been created for a pothole, update the expiry date for the pothole.
                #Attempt to update the expiry date of the pothole.
                try:
                    #Update the expiry date of the pothole, add the pothole to the database, and commit the changes.
                    finalPothole.expiryDate = datetime.now() + timedelta(days=EXPIRY_DATE_REFRESH)
                    db.session.add(finalPothole)
                    db.session.commit()
                except:
                #Otherwise, if an error has occurred, rollback the changes and return an error message and an "INTERNAL SERVER ERROR" http status code (500).
                    db.session.rollback()
                    return {"error": "Unable to update expiry date!"}, 500
            #Otherwise, if a report cannto be created for the pothole, rollback the changes and return an error message and an "INTERNAL SERVER ERROR" http status code (500).
            except:
                db.session.rollback()
                return {"error": "Unable to add report to database! Ensure that all fields are filled out."}, 500

            return {"message" : "Successfully added pothole report to database!"}, 201
        #Otherwise, the coordinates reported are outside of Trinidad and Tobago. Return an error and 'BAD REQUEST' http status code (400).
        else:
            return {"error" : "The coordinates are not in Trinidad and Tobago!"}, 400
    #Otherwise, the request does not contain all of the required fields for processing. Return an error and 'BAD REQUEST' http status code (400).
    else:
        return {"error" : "Invalid report details submitted!"}, 400

#Validates a report of a user via the driver interface before adding it to the database.
def reportPotholeDriver(user, reportDetails):
    #Initializes the finalPothole to be added to None.
    finalPothole = None
    
    #Determines if the reportDetails contains all of the neccesary fields for processing of the report.
    if "longitude" in reportDetails and "latitude" in reportDetails:
        #If the coordinates reported are within the bounds for Trinidad and Tobago, process the report.
        if -61.965556 < reportDetails["longitude"] < -60.469077 and 10.028088 < reportDetails["latitude"] < 11.370345:
            #Finds the closest pothole to the coordinates.
            finalPothole = findClosestPothole(reportDetails["latitude"], reportDetails["longitude"])

            #If there does not exist an existing pothole that the report can be mapped to, create a new pothole at the report location.
            if not finalPothole:
                #Attempts to create a pothole record using the report details.
                try:
                    #Creates the report using the report details, adds the report to the database, and commits the changes.
                    newPothole = Pothole(longitude=reportDetails["longitude"], latitude=reportDetails["latitude"], expiryDate=datetime.now() + timedelta(days=EXPIRY_DATE_PRIMARY))
                    db.session.add(newPothole)
                    db.session.commit()
                    #Sets the selected finalPothole to this new pothole object.
                    finalPothole = newPothole
                #Otherwise, if a pothole cannot be created, rollback the database and return an error with 'INTERNAL SERVER ERROR' status code.
                except:
                    db.session.rollback()
                    return {"error": "Error adding pothole to database!"}, 500
            #Otherwise, if there exists an existing pothole that the report can be mapped to, create a report for that location.
            else:
                #Determines if a report has already been submitted by the user for this pothole.
                alreadySubmitted = db.session.query(Report).filter_by(userID=user.userID, potholeID=finalPothole.potholeID).first()
                #If a report has already been submitted, a resubmission will reset the expiry date of the pothole.
                if alreadySubmitted:
                    #Updates the expiry date of the pothole by adding a constant number of days to the expiry date.
                    try:
                        #Updates expiry date, adds and commits changes to database. Returns a success message and a 'CREATED' http status code (201).
                        finalPothole.expiryDate = datetime.now() + timedelta(days=EXPIRY_DATE_REFRESH)
                        db.session.add(finalPothole)
                        db.session.commit()
                        return {"message" : "Expiry date of pothole has been reset!"}, 201
                    except:
                    #Otherwise, the pothole could not be updated. Rollback the database and return an error with a 'INTERNAL SERVER ERROR' https tatus code (500).
                        db.session.rollback()
                        return {"error": "Unable to update expiry date!"}, 500
            #Attempts to create a report for the pothole.
            try:
                #Creates a new report for the finalPothole using the description.
                newReport = Report(userID = user.userID, potholeID=finalPothole.potholeID, description="Pothole submitted via Driver Mode.")
                db.session.add(newReport)
                db.session.commit()

                #Update the expiry date of the pothole, add the pothole to the database, and commit the changes.
                try:
                    finalPothole.expiryDate = datetime.now() + timedelta(days=30)
                    db.session.add(finalPothole)
                    db.session.commit()
                 #Otherwise, if an error has occurred, rollback the changes and return an error message and an "INTERNAL SERVER ERROR" http status code (500).
                except:
                    db.session.rollback()
                    return {"error": "Unable to update expiry date!"}, 500
            #Otherwise, if a report cannot be created, rollback the database and return an error and a 'INTERNAL SERVER ERROR' http status code (500).
            except:
                db.session.rollback()
                return {"error": "Unable to add report to database!"}, 500

            #Once the report and expiry dates have been succesfully added and updated, return a success message and a 'CREATED' http status code (201)
            return {"message" : "Successfully added pothole report to database!"}, 201

        #Otherwise, the coordinates reported are outside of Trinidad and Tobago. Return an error and 'BAD REQUEST' http status code (400).
        else:
            return {"error" : "The coordinates are not in Trinidad and Tobago!"}, 400
    #Otherwise, the request does not contain all of the required fields for processing. Return an error and 'BAD REQUEST' http status code (400).
    else:
        return {"error" : "Invalid report details submitted!"}, 400


#SYSTEM POTHOLE REPORT DELETE FUNCTION
#Allows the system to delete a pothhole given the reportID and potholeID.
def deletePotholeReport(potholeID, reportID):
    #If the potholeID or reportID is invalid, return False
    if(not potholeID or not reportID):
        return False

    #Finds and stores the report to be deleted using the potholeID and reportID.
    foundReport = db.session.query(Report).filter_by(potholeID= potholeID, reportID=reportID).first()

    #If the report is found, delete the report.
    if foundReport:
        #Attempts to delete the report.
        try:
            #Deletes the report and commits the change to the database.
            db.session.delete(foundReport)
            db.session.commit()

            #Determines if there are any reports for a pothole given the potholeID.
            potholeReports = db.session.query(Report).filter_by(potholeID = potholeID).first()
            #If there is no report found, the pothole has no more reports and can therefore be deleted.
            if not potholeReports:
                deletePothole(potholeID)

            #Returns true since the report was deleted.
            return True
        #If the deletion fails, rollback the database and return false since there was no deletion.
        except:
            db.session.rollback()
            return False
    #If the report is not found, return false since there was no deletion.
    else:
        return False

#USER POTHOLE REPORT DELETE FUNCTION
#Facilitates the creator of a report to be able to delete their own report.
def deleteUserPotholeReport(user, potholeID, reportID):
    #Ensures that the potholeID and reportID are non-null before deleting the data.
    if potholeID and reportID:
        #Finds the report, reported by the user, that corresponds to the potholeID and reportID.
        foundReport = db.session.query(Report).filter_by(potholeID=potholeID, reportID=reportID, userID=user.userID).first()

        #If a report is found, delete the report.
        if foundReport:
            #Attempts to delete the found report and commit to database.
            try:
                db.session.delete(foundReport)
                db.session.commit()

                #Determines if there are any more reports for the pothole after the deletion.
                potholeReports = db.session.query(Report).filter_by(potholeID = potholeID).first()
                #If there are no more reports for that pothole, the pothole can be deleted.
                if not potholeReports:
                    #Deletes the pothole with the specified ID.
                    deletePothole(potholeID)
                
                #After deleting the reports/pothole, return a success message and a 'OK' http status code (200).
                return {"message" : "Successfully deleted report."}, 200
            #If deleting the report fails, rollback the database, and return an error and 'INTERNAL SERVER ERROR' http status code (500).
            except:
                db.session.rollback()
                return {"error" : "Unable to delete report."}, 500
        #Otherwise, if a report was not found, return an error and a 'NOT FOUND' http status code (404).
        else:
            return {"error" : "Report does not exist! Unable to delete."}, 404
    #Otherwise, if the potholeID or the reportID are null, an invalid request was submitted. Return an error message and a 'BAD REQUEST' http status request (400).
    else:
        return {"error" : "Invalid report details provided."}, 400

#Facilitates the creator of a report to update the description of their report.    
def updateReportDescription(user, potholeID, reportID, potholeDetails):
    #Determines if the potholeDetails is not null before processing the data.
    if potholeDetails:
        #If the potholeDetails contains a "description" key field, process the data.
        if "description" in potholeDetails:
            #Finds the report, made by the creator, that is specified by the potholeID and reportID.
            report = db.session.query(Report).filter_by(userID=user.userID, reportID=reportID, potholeID=potholeID).first()
            #If a report is found, update the description.
            if report:
                #Attempts to update the description of the found report, add the report to the database, and commit the changes.
                #Also returns a message and a 'OK' http status code (200).
                try:
                    report.description = potholeDetails["description"]
                    db.session.add(report)
                    db.session.commit()
                    return {"message" : "Pothole report description updated!"}, 200
                #If the report cannot be updated, rollback the database, and return an error and 'INTERNAL SERVER ERROR' http status code (500).
                except:
                    db.session.rollback()
                    return {"error": "Unable to update expiry date!"}, 500
            #Otherwise, if a report is not found, return an error and a 'NOT FOUND' http status code.
            else:
                return {"error" : "Report does not exist!"}, 404
        #Otherwise, potholeDetails does not contain a description and cannot be used to update the description.
        #Return an error and 'BAD REQUEST' http status code (400).
        else:
            return {"error" : "Invalid report details submitted!"}, 400
    #Otherwise, reportDetails is null and cannot be processed. Return an error and 'BAD REQUEST' status code.
    else:
        return {"error" : "Invalid report update request submitted!"}, 400


#Returns an json dump of the array of all the reports associated with a potholeID.
def getPotholeReports(potholeID):
    #If the potholeID or reportID is invalid, return an error and BAD REQUEST status code (400)
    if(not potholeID):
        return json.dumps({"error": "Invalid pothole ID specified."}), 400

    #Gets all of the reports associated with a potholeID.
    reports = db.session.query(Report).filter_by(potholeID=potholeID).all()
    #Converts all of the found reports to their dictionary definition, and stores them in an array.
    reportData = [r.toDict() for r in reports]
    #Returns all of the reports in an array in json form, and an 'OK' http status codee (200).
    return json.dumps(reportData), 200

#Returns an individual pothole information given the potholeID and reportID.
def getIndividualPotholeReport(potholeID, reportID):
    #If the potholeID or reportID is invalid, return an error and BAD REQUEST status code (400)
    if(not potholeID or not reportID):
        return json.dumps({"error": "Invalid pothole ID or report ID specified."}), 400

    #Gets the report associated with the potholeID and reportID.
    report = db.session.query(Report).filter_by(potholeID=potholeID, reportID=reportID).first()
    #If a report is found, return a json dump of the definition of the report and a 'OK' http status code (200).
    if(report):
        return json.dumps(report.toDict()), 200
    #Otherwise, if a report is not found, return an error and a 'NOT FOUND' http status code (404).
    else:
        return json.dumps({"error": "No report found."}), 404


##################### TEST CONTROLLERS #####################

def getAllPotholeReportsByUser(user):
    if(not user):
        return []
        
    allReports = db.session.query(Report).filter_by(userID=user.userID).all()
    allReports = [r.toDict() for r in allReports]
    return allReports