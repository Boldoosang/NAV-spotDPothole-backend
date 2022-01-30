#Justin Baldeosingh
#SpotDPothole-Backend
#NULLIFY

#USER VIEW - Defines the view endpoints for REPORTEDIMAGES.

#Imports flask modules.
from flask_jwt_extended import jwt_required, current_user
from flask import Blueprint, request, jsonify, send_from_directory



#Creates a blueprint to the collection of views for users.
userViews = Blueprint('userViews', __name__)

#Imports the all of the controllers of the application.
from App.controllers import *
from App.controllers.user import changePassword, identifyUser, loginUserController, registerUserController

#Creates a POST route to facilitate the registration of a new user. Also returns a status code to denote the outcome of the operation.
@userViews.route('/register', methods=["POST"])
def registerUserView():
    regData = request.get_json()
    outcomeMessage, statusCode = registerUserController(regData)
    return json.dumps(outcomeMessage), statusCode

#Creates a POST route to facilitate the login of an existing user. Also returns a status code to denote the outcome of the operation.
@userViews.route('/login', methods=["POST"])
def loginUserView():
    loginDetails = request.get_json()
    outcomeMessage, statusCode = loginUserController(loginDetails)
    return json.dumps(outcomeMessage), statusCode

#Creates a PUT route to facilitate the change of a password of an existing user. Also returns a status code to denote the outcome of the operation.
@userViews.route('/user', methods=["PUT"])
@jwt_required()
def changePasswordView():
    passwordDetails = request.get_json()
    outcomeMessage, statusCode = changePassword(current_user, passwordDetails)
    return json.dumps(outcomeMessage), statusCode


#Creates a GET route to return the details of the current user. Also returns a status code to denote the outcome of the operation.
@userViews.route("/identify", methods=["GET"])
#Ensures that this route is only accessible to logged in users.
@jwt_required()
def identify():
    outcomeMessage, statusCode = identifyUser(current_user)
    return json.dumps(outcomeMessage), statusCode
