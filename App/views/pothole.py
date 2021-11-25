#Justin Baldeosingh
#SpotDPothole-Backend
#NULLIFY

#POTHOLE VIEW - Defines the view endpoints for POTHOLES.

#Imports flask modules.
from flask import Blueprint, redirect, request, jsonify, send_from_directory

from App.controllers.pothole import getIndividualPotholeData, getPotholeData, nukePotholesInDB

#Creates a blueprint to the collection of views for potholes.
potholeViews = Blueprint('potholeViews', __name__)

#Imports the all of the controllers of the application.
from App.controllers import *

#Creates a GET route for the retrieval of all of the pothole data. Also returns a status code to denote the outcome of the operation.
@potholeViews.route('/api/potholes', methods=["GET"])
def displayPotholes():
    displayData, statusCode = getPotholeData()
    return displayData, statusCode

#Creates a GET route for the retrieval of a single pothole's data. Also returns a status code to denote the outcome of the operation.
@potholeViews.route('/api/potholes/<id>', methods=["GET"])
def displayIndividualPotholes(id):
    displayData, statusCode = getIndividualPotholeData(id)
    return displayData, statusCode



############# TEST ROUTES ##############
@potholeViews.route('/nuke', methods=["GET"])
def nukePotholes():
    nukePotholesInDB()
    return json.dumps("Nuked"), 200