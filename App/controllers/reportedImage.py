#Justin Baldeosingh
#SpotDPothole-Backend
#NULLIFY

#REPORTEDIMAGE CONTROLLERS - Facilitate interactions between the reportedImage model and the other models/controllers of the application.

#Imports sqlalchemy errors, requests and json.
from sqlalchemy.exc import IntegrityError
import json, requests
import filetype, os, time, random, base64, tempfile, string

#Imports the all of the required models, controllers, and functions.
from App.models import *
from App.controllers import *
from PIL import Image
from io import BytesIO
from werkzeug.utils import secure_filename
from pyrebase import pyrebase
from App.firebaseConfig import config

#Initializes the firebase object, storage object, and main directory for use in storing images.
firebase = pyrebase.initialize_app(config)
storage = firebase.storage()
MYDIR = os.path.dirname(__file__)

#Allows for the uploading of an image given a base64 encoded string.
def uploadImage(base64Image, Testing=False):
    #Attempts to process the base64 image and upload it to firebase.
    
    try:
        #Obtains the data portion of the base64 image string.
        fileData = str(base64Image).split("base64")[1]

        #Generates randomized filename for firebase
        milliseconds = int(time.time() * 1000)
        randomString = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        new_filename = "REPORT " + str(milliseconds) + "_" + randomString + ".jpg"

        #Creates a temporary file for use in storing the images.
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg", dir=os.path.join(os.getcwd(), "App/uploads"))


        #Decodes the base64 image and opens it using PIL.
        im = Image.open(BytesIO(base64.b64decode(fileData)))
        #Discards the alpha channel of the image
        im = im.convert("RGB")
        #Saves the image using the temporary file.
        im.save(temp.name)

        #Determines if the MIME type of the file corresponds to an image and returns an error otherwise.
        if not filetype.is_image(temp.name):
            return "invalid image"
        
        #Opens the saved image at the temporary location.
        image = Image.open(temp.name)

        #Sets the new dimensions of the image; preserving the aspect ratio.
        height = int(480)
        width = int(height / image.height * image.width)
        resizedImage = image.resize((width, height))

        #Compresses the image and removes transparency.
        resizedImage = resizedImage.convert("RGB")

        #Saves the image as a JPEG at the temporary location.
        resizedImage.save(temp.name, format="JPEG")
        print("Written to file!")

        #Uses the main directory if not in testing mode. Otherwise, uses the testing directory.
        cloudDirectory = "images/"
        if Testing:
            cloudDirectory = "test/"

        #Stores the image at the directory in the firebase cloud storage bucket.
        storage.child(cloudDirectory + new_filename).put(temp.name)

        #Obtains a link for the newly stored image.
        link = storage.child(cloudDirectory + new_filename).get_url(None)

        #Prints and returns the link to the uploaded image.
        print("Uploaded to cloud via: " + link)
        return link

    except:
    #Otherwise, if the image could not be uploaded, return null.
        return null

#Deletes an image from the firebase storage, if it exists.
def deleteImageFromStorage(imageID):
    #Attempts to delete an image from the firebase storage given an imageID, if it exists.
    try:
        #Obtains the image link corresponding to the imageID.
        image = db.session.query(ReportedImage).filter_by(imageID = imageID).first()

        #Obtains the path of the image on the firebase storage.
        filePath = image.imageURL.split("/")[-1].split("?")[0]
        filePath = filePath.replace("%2F", "/").replace("%20", " ")

        #Deletes the file from firebase storage, prints a success message, and returns True.
        storage.delete(filePath, None)
        print("Successfully deleted this image!")
        return True
    except:
    #Otherwise the image could not be deleted. Rollback the database, print an error message and return False.
        db.session.rollback()
        print("Unable to delete this image!")
        return False

#Deletes all of the report images for a particular report.
def deleteAllReportImagesFromStorage(reportID):
    #Attempts to delete the images for a particular report given the reportID, if it exists.
    try:
        #Gets all of the images corresponding with a reportID and deletes them.
        images = db.session.query(ReportedImage).filter_by(reportID = reportID).all()
        for image in images:
            deleteImageFromStorage(image.imageID)
    except:
    #Otherwise, rollback the database and print an error message.
        db.session.rollback()
        print("Unable to delete all report images!")

#Deletes all of the report images for a particular pothole.
def deleteAllPotholeImagesFromStorage(potholeID):
    #Attempts to delete the images for a particular pothole given the potholeID, if it exists.
    try:
        #Gets all of the images corresponding with a potholeID and deletes them.
        images = db.session.query(ReportedImage).filter_by(potholeID = potholeID).all()
        for image in images:
            deleteImageFromStorage(image.imageID)
    except:
        #Otherwise, rollback the database and print an error message.
        db.session.rollback()
        print("Unable to delete all pothole images!")

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
            if user.banned:
                return {"error": "User is banned."}, 403

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
                #Deletes the found image from the database, commits the change, and returns a success message along with a 'OK' http status code.
                deleteImageFromStorage(foundImage.imageID)
                db.session.delete(foundImage)
                db.session.commit()
                
                return {"message" : "Pothole image successfully deleted!"}, 200
            except Exception as e:
            #If an error has occurred, rollback the database and return an error and an "INTERNAL SERVER ERROR" http status code.
                print(e)
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
def addPotholeReportImage(user, potholeID, reportID, imageDetails, Testing=False):
    #Attempts to add the report image to a particular report.
    try:
        #If the user, reportID and imageDetails are non null, facilitate the addition of the image.
        if user and reportID and imageDetails:
            if user.banned:
                return {"error": "User is banned."}, 403

            #If the imageDetails contains an "images" attribute, it meets the format request. Proceed with facilitating image addition.
            if "images" in imageDetails:
                #Finds report, for the user, that corresponds with the reportID and potholeID.
                foundReport = db.session.query(Report).filter_by(userID=user.userID, reportID=reportID, potholeID = potholeID).first()

                #If no report was found for the user, return an error to the user and a 'NOT FOUND' http status code.
                if not foundReport:
                    return {"error" : "You are not the creator of this report!"}, 404

                #Sets invalidCount to 0 to denote that no images have failed to be added to the database.
                invalidCount = 0
                #Iterates over the different image URLs in the user request.
                for base64Image in imageDetails["images"]:

                    imageURL = uploadImage(base64Image, Testing=Testing)
                    #If the URL points to an image, add the image to the database.
                    if is_url_image(imageURL):
                        #Attempts to add the image to the database.
                        try:
                            #Adds the image for the report to the database using the URL and reportID.
                            reportImage = ReportedImage(reportID=foundReport.reportID, imageURL=imageURL)
                            db.session.add(reportImage)
                            db.session.commit()
                            print("Pothole image succesfully added!")
                        #If an entry with the same URL exists, rollback the error, count the invalid entry, and print an error message.
                        except IntegrityError:
                            db.session.rollback()
                            invalidCount += 1
                            print("Pothole image already exists!")
                        #Otherwise if an unknown error is found, count the invalid entry and print an error message.
                        except:
                            invalidCount += 1
                            db.session.rollback()
                            print("Pothole image could not be added.")
                    else:
                        invalidCount += 1
                
                #If the invalid count is greater than 0, return the outcome along with a 'PARTIAL CONTENT' http status code (206).
                if invalidCount > 0:
                    return {"error" : "One or more images were not succesfully added."}, 206
                #Otherwise, return a success message and a 'CREATED' http status code (201).
                else:
                    return {"message" : "All images successfully added."}, 201
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
