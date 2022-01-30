#Justin Baldeosingh
#SpotDPothole-Backend
#NULLIFY

#REPORT VIEW - Defines the view endpoints for REPORTS.

#Imports flask modules.
from flask_jwt_extended import current_user, jwt_required
from flask import Blueprint, redirect, request, jsonify, send_from_directory

from App.controllers.report import deleteUserPotholeReport, getIndividualPotholeReport, getPotholeReports, getReportData, getReportDataForUser, updateReportDescription

#Creates a blueprint to the collection of views for reports.
reportViews = Blueprint('reportViews', __name__)

#Imports the all of the controllers of the application.
from App.controllers import *

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