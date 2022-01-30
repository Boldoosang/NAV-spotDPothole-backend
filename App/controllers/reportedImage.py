#Justin Baldeosingh
#SpotDPothole-Backend
#NULLIFY

#REPORTEDIMAGE CONTROLLERS - Facilitate interactions between the reportedImage model and the other models/controllers of the application.

#Imports sqlalchemy errors, requests and json.
import string
from sqlalchemy.exc import IntegrityError
import json, requests

#Imports the all of the required models and controllers.
from App.models import *
from App.controllers import *


#TEST



from pyrebase import pyrebase
from PIL import Image
from App.firebaseConfig import config
import tempfile
import filetype, os, time
import random
from werkzeug.utils import secure_filename
from flask_jwt_extended import current_user, jwt_required

firebase = pyrebase.initialize_app(config)

storage = firebase.storage()

MYDIR = os.path.dirname(__file__)



def uploadImage(files):
    
    databaseURLs = []
    fallbackURLs = []

    try:
        for indivFile in files:
            file = indivFile
            filename = secure_filename(file.filename)

            #Generates filename for firebase
            milliseconds = int(time.time() * 1000)
            randomString = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            new_filename = "REPORT " + str(milliseconds) + "_" + randomString + ".jpg"


            temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg", dir=os.path.join(os.getcwd(), "App/uploads"))
            file.save(temp.name)

            if not filetype.is_image(temp.name):
                return {"error" : "One of the files is not an image!"}, 400
            
            image = Image.open(temp.name)

            height = int(480)
            width = int(height / image.height * image.width)

            resizedImage = image.resize((width, height))
            resizedImage = resizedImage.convert("RGB")
            resizedImage.save(temp.name, format="JPEG")

            storage.child("images/" + new_filename).put(temp.name)

        
            link = storage.child("images/" + new_filename).get_url(None)
            databaseURLs.append(link)
            fallbackURLs.append(link.split("/")[-1].split("?")[0])
            
    except:
        for dbFilename in fallbackURLs:
            filePath = dbFilename.replace("%2F", "/").replace("%20", " ")
            print(filePath)
            storage.delete(filePath, None)

        return "error"
        

    return databaseURLs


def deleteImageFromStorage(imageID):
    try:
        image = db.session.query(ReportedImage).filter_by(imageID = imageID).first()
        filePath = image.imageURL.split("/")[-1].split("?")[0]
        filePath = filePath.replace("%2F", "/").replace("%20", " ")

        print(filePath)
        storage.delete(filePath, None)
        print("Successfully deleted this image!")
        return True
    except:
        db.session.rollback()
        print("Unable to delete this image!")
        return False

def deleteAllReportImagesFromStorage(reportID):
    try:
        images = db.session.query(ReportedImage).filter_by(reportID = reportID).all()
        for image in images:
            deleteImageFromStorage(image.imageID)
    except:
        db.session.rollback()
        print("Unable to delete all report images!")

def deleteAllPotholeImagesFromStorage(potholeID):
    try:
        images = db.session.query(ReportedImage).filter_by(potholeID = potholeID).all()
        for image in images:
            deleteImageFromStorage(image.imageID)
    except:
        db.session.rollback()
        print("Unable to delete all pothole images!")
#TEST

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

#Finds and returns the json dump of all of the images corresponding to a particular reportID.
def getPotholeReportImages(reportID):
    #Attempts to get pothole images for a particular report.
    try:
        #If the reportID is not null, find the report images.
        if reportID:
            #Finds all of the images for a report that correspond with the reportID, and returns the json dump of the image toDicts.
            #Also returns the 'OK' http status code (200).
            foundReportedImages = db.session.query(ReportedImage).filter_by(reportID=reportID).all()
            return json.dumps([image.toDict() for image in foundReportedImages]), 200
        #Otherwise, an invalid reportID was submitted. Return an error message and a 'BAD REQUEST' http status code (400).
        else:
            db.session.rollback()
            return {"error" : "Invalid pothole image requested!"}, 400
    except:
    #If the images cannot be retrieved (invalid datatype used for querying), rollback the databse and return an error.
        db.session.rollback()
        return {"error": "Invalid report ID specified."}, 400

#Finds and returns the image information corresponding to a particular reportID and imageID.
def getIndividualPotholeReportImage(reportID, imageID):
    #Attempts to get the report image for a particular report.
    try:
        #If both reportID and imageID are not null, find and return the image information.
        if reportID and imageID:
            #Finds the image in the database given the imageID and reportID.
            foundReportedImage = db.session.query(ReportedImage).filter_by(imageID=imageID, reportID=reportID).first()

            #If no reported image is found, return an appropriate error and a 'NOT FOUND" http status code.
            if not foundReportedImage:
                return {"error" : "Pothole image not found!"}, 404

            #Otherwise, return the information for the found reported image, and 'OK' http status code.
            return json.dumps(foundReportedImage.toDict()), 200
        #If either of the reportID or imageID are null, return an error and 'BAD REQUEST' http status code.
        else:
            db.session.rollback()
            return {"error" : "Invalid pothole image requested!"}, 400
    except:
    #If the image cannot be retrieved (invalid datatype used for querying), rollback the databse and return an error.
        db.session.rollback()
        return {"error": "Invalid report ID or imageID specified."}, 400

#For the original posting user, facilitates the deletion of an image for a report.
def deletePotholeReportImage(user, potholeID, reportID, imageID):
    #Attempts to get the report images for a particular report.
    try:
        #If the user, reportID and imageID are not null, facilitate the deletion.
        if user and reportID and imageID:
            #Finds the report, posted by the user, that matches the reportID and potholeID.
            foundReport = db.session.query(Report).filter_by(userID=user.userID, reportID=reportID, potholeID = potholeID).first()

            #If there is no found report, return an error message and a 'NOT FOUND' http status code (404).
            if not foundReport:
                return {"error" : "You are not the creator of this report!"}, 404

            #Finds the image of a report, given the reportID and imageID.
            foundImage = db.session.query(ReportedImage).filter_by(reportID=reportID, imageID=imageID).first()

            #If there is no found image, return an error message and a 'NOT FOUND' http status code (404).
            if not foundImage:
                return {"error" : "This image does not exist!"}, 404

            #Attempts to delete the found image from the database.
            try:
                deleteImageFromStorage(foundImage.imageID)
                #Deletes the found image from the database, commits the change, and returns a success message along with a 'OK' http status code.
                db.session.delete(foundImage)
                db.session.commit()
                
                return {"message" : "Pothole image successfully deleted!"}, 200
            except:
            #If an error has occurred, rollback the database and return an error and an "INTERNAL SERVER ERROR" http status code.
                db.session.rollback()
                return {"error" : "Unable to delete report!"}, 500

        #If any of the user, reportID and imageID values are null, return an error and a 'BAD REQUEST' http status code.    
        else:
            db.session.rollback()
            return {"error" : "Invalid pothole image submitted!"}, 400
    except:
    #If the images cannot be retrieved (invalid datatype used for querying), rollback the databse and return an error.
        db.session.rollback()
        return {"error": "Invalid request submitted."}, 400

#For the original report poster, adds an image to their report given the imageDetails.
def addPotholeReportImage(user, potholeID, reportID, files):
    #Attempts to add the report image to a particular report.
    try:
        #If the user, reportID and imageDetails are non null, facilitate the addition of the image.
        if user and reportID:
            #If the imageDetails contains an "images" attribute, it meets the format request. Proceed with facilitating image addition.
            if files:
                uploadedImages = uploadImage(files)

                if uploadedImages != "error":
                    #Finds report, for the user, that corresponds with the reportID and potholeID.
                    foundReport = db.session.query(Report).filter_by(userID=user.userID, reportID=reportID, potholeID = potholeID).first()

                    #If no report was found for the user, return an error to the user and a 'NOT FOUND' http status code.
                    if not foundReport:
                        return {"error" : "You are not the creator of this report!"}, 404

                    #Iterates over the different image URLs in the user request.
                    for imageURL in uploadedImages:
                        #Attempts to add the image to the database.
                        try:
                            #Adds the image for the report to the database using the URL and reportID.
                            reportImage = ReportedImage(reportID=foundReport.reportID, imageURL=imageURL)
                            db.session.add(reportImage)
                            db.session.commit()
                            print("Pothole image succesfully added!")
                            return {"message" : "All images successfully added."}, 201
                        #Otherwise if an unknown error is found, count the invalid entry and print an error message.
                        except:
                            db.session.rollback()
                            print("Pothole image could not be added.")
                            #If the invalid count is greater than 0, return the outcome along with a 'PARTIAL CONTENT' http status code (206).
                            return {"error" : "Unable to add all images."}, 206   
                else:
                    return {"error" : "Unable to upload all images to the database!"}, 400  
            #If there is no 'images' key field in the dictionary, the request is empty. Return an error message and a 'BAD REQUEST' http status code.
            else:
                return {"error" : "No pothole images submitted!"}, 400
        #If any of the the user, reportID and imageDetails are null, return an error message and a 'BAD REQUEST' http status code (400).
        else:
            db.session.rollback()
            return {"error" : "Invalid pothole request submitted!"}, 400
    except:
    #If the image cannot be added (invalid datatype used for adding), rollback the databse and return an error.
        db.session.rollback()
        return {"error": "Invalid request submitted."}, 400
