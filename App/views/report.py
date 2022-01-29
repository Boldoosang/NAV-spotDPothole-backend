#Justin Baldeosingh
#SpotDPothole-Backend
#NULLIFY

#REPORT VIEW - Defines the view endpoints for REPORTS.

#Imports flask modules.

import random
import string
from flask_jwt_extended import current_user, jwt_required
from flask import Blueprint, redirect, request, jsonify, send_from_directory, url_for
import os
from werkzeug.utils import secure_filename
from App.controllers.report import deleteUserPotholeReport, getIndividualPotholeReport, getPotholeReports, getReportData, getReportDataForUser, updateReportDescription

#Creates a blueprint to the collection of views for reports.
reportViews = Blueprint('reportViews', __name__)

#Imports the all of the controllers of the application.
from App.controllers import *

import time

#TESTING

from pyrebase import pyrebase
from PIL import Image
from App.firebaseConfig import config
import tempfile
import filetype

firebase = pyrebase.initialize_app(config)

storage = firebase.storage()



ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
MYDIR = os.path.dirname(__file__)

@reportViews.route("/testUpload", methods=["POST"])
def handleTestUpload():
    print(request.files['file'])
    file = request.files['file']
    filename = secure_filename(file.filename)

    

    #Generates filename for firebase
    milliseconds = int(time.time() * 1000)
    randomString = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    new_filename = "REPORT " + str(milliseconds) + "_" + randomString + ".jpg"


    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg", dir=os.path.join(os.getcwd(), "App/uploads"))
    file.save(temp.name)

    if not filetype.is_image(temp.name):
        return {"error" : "File is not an image!"}, 400
    
    image = Image.open(temp.name)

    height = int(480)
    width = int(height / image.height * image.width)

    resizedImage = image.resize((width, height))

    resizedImage.save(temp.name, "JPEG")

    storage.child("images/" + new_filename).put(temp.name)

    directory, filename = os.path.split(temp.name)
    print(filename)

    link = storage.child("images/" + new_filename).get_url(None)

    print(link)
    #storage.delete("images/" + new_filename, None)

    return "success"











#Creates a GET route for the retrieval of all of the report data. Also returns a status code to denote the outcome of the operation.
@reportViews.route('/api/reports', methods=["GET"])
def displayReports():
    displayData, statusCode = getReportData()
    return displayData, statusCode

#Creates a GET route for the retrieval of all of the report data for a particular pothole. Also returns a status code to denote the outcome of the operation.
@reportViews.route('/api/reports/pothole/<potholeID>', methods=["GET"])
def displayPotholeReports(potholeID):
    displayData, statusCode = getPotholeReports(potholeID)
    return displayData, statusCode

#Creates a GET route for the retrieval of an individual report of a pothole. Also returns a status code to denote the outcome of the operation.
@reportViews.route('/api/reports/pothole/<potholeID>/report/<reportID>', methods=["GET"])
def displayIndividualPotholeReport(potholeID, reportID):
    displayData, statusCode = getIndividualPotholeReport(potholeID, reportID)
    return displayData, statusCode

#Creates a PUT route for the updating of an individual report of a pothole. Also returns a status code to denote the outcome of the operation.
@reportViews.route('/api/reports/pothole/<potholeID>/report/<reportID>', methods=["PUT"])
#Ensures that this route is only accessible to logged in users.
@jwt_required()
def updatePotholeReportDescription(potholeID, reportID):
    potholeDetails = request.get_json()
    outcomeMessage, statusCode = updateReportDescription(current_user, potholeID, reportID, potholeDetails)
    return outcomeMessage, statusCode

#Creates a DELETE route for the deletion of an individual report of a pothole. Also returns a status code to denote the outcome of the operation.
@reportViews.route('/api/reports/pothole/<potholeID>/report/<reportID>', methods=["DELETE"])
#Ensures that this route is only accessible to logged in users.
@jwt_required()
def deletePotholeReport(potholeID, reportID):
    outcomeMessage, statusCode = deleteUserPotholeReport(current_user, potholeID, reportID)
    return outcomeMessage, statusCode

#Creates a POST route for the creating of a report of a pothole via the standard interface. Also returns a status code to denote the outcome of the operation.
@reportViews.route('/api/reports/standard', methods=["POST"])
#Ensures that this route is only accessible to logged in users.
@jwt_required()
def standardReport():
    reportDetails = request.get_json()
    outcomeMessage, statusCode = reportPotholeStandard(current_user, reportDetails)
    return json.dumps(outcomeMessage), statusCode

#Creates a POST route for the creating of a report of a pothole via the driver interface. Also returns a status code to denote the outcome of the operation.
@reportViews.route('/api/reports/driver', methods=["POST"])
#Ensures that this route is only accessible to logged in users.
@jwt_required()
def driverReport():
    reportDetails = request.get_json()
    outcomeMessage, statusCode = reportPotholeDriver(current_user, reportDetails)
    return json.dumps(outcomeMessage), statusCode