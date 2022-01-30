#Justin Baldeosingh
#SpotDPothole-Backend
#NULLIFY

#REPORTEDIMAGE VIEW - Defines the view endpoints for REPORTEDIMAGES.

#Imports flask modules.
from flask_jwt_extended import current_user, jwt_required
from flask import Blueprint, redirect, request, jsonify, send_from_directory

#Creates a blueprint to the collection of views for reportedImages.
reportedImageViews = Blueprint('reportedImageViews', __name__)

#Imports the all of the controllers of the application.
from App.controllers import *

#Creates a GET route for the retrieval of an individual reported image of a report. Also returns a status code to denote the outcome of the operation.
@reportedImageViews.route('/api/reports/pothole/<potholeID>/report/<reportID>/images/<imageID>', methods=["GET"])
def getIndividualReportedImage(potholeID, reportID, imageID):
    displayData, statusCode = getIndividualPotholeReportImage(reportID, imageID)
    return displayData, statusCode

#Creates a GET route for the retrieval of all of the reported image of a report. Also returns a status code to denote the outcome of the operation.
@reportedImageViews.route('/api/reports/pothole/<potholeID>/report/<reportID>/images', methods=["GET"])
def getReportImages(potholeID, reportID):
    displayData, statusCode = getPotholeReportImages(reportID)
    return displayData, statusCode

#Creates a DELETE route for the deletion of the individual reported image of a report. Also returns a status code to denote the outcome of the operation.
@reportedImageViews.route('/api/reports/pothole/<potholeID>/report/<reportID>/images/<imageID>', methods=["DELETE"])
#Ensures that this route is only accessible to logged in users.
@jwt_required()
def deletePotholeImage(potholeID, reportID, imageID):
    displayData, statusCode = deletePotholeReportImage(current_user, potholeID, reportID, imageID)
    return displayData, statusCode


#Creates a POST route for the addition of a reported image to a report. Also returns a status code to denote the outcome of the operation.
@reportedImageViews.route('/api/reports/pothole/<potholeID>/report/<reportID>/images', methods=["POST"])
#Ensures that this route is only accessible to logged in users.
@jwt_required()
def addPotholeImage(potholeID, reportID):
    files = request.files.getlist("images")
    displayData, statusCode = addPotholeReportImage(current_user, potholeID, reportID, files)
    return displayData, statusCode