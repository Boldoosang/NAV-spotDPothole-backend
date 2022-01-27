#Justin Baldeosingh
#SpotDPothole-Backend
#NULLIFY

#DASHBOARD VIEW - Defines the view endpoints for the dashboard.

#Imports flask modules.
from flask_jwt_extended import current_user, jwt_required
from flask import Blueprint, redirect, request, jsonify, send_from_directory

#Imports controllers
from App.controllers.pothole import getUserPotholeData
from App.controllers.report import getReportDataForUser


#Creates a blueprint to the collection of views for reports.
dashboardViews = Blueprint('dashboardViews', __name__)


#Creates a GET route for the retrieval of a user's pothole data. Also returns a status code to denote the outcome of the operation.
@dashboardViews.route('/api/dashboard/potholes', methods=["GET"])
@jwt_required()
def displayUserPotholes():
    displayData, statusCode = getUserPotholeData(current_user)
    return displayData, statusCode

#Creates a GET route for the retrieval of all of the report data. Also returns a status code to denote the outcome of the operation.
@dashboardViews.route('/api/dashboard/reports', methods=["GET"])
@jwt_required()
def displayUserReports():
    displayData, statusCode = getReportDataForUser(current_user)
    return displayData, statusCode