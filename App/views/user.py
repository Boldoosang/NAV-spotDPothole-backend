#Justin Baldeosingh
#SpotDPothole-Backend
#NULLIFY

#USER VIEW - Defines the view endpoints for USER.

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
@userViews.route('/user/password', methods=["PUT"])
@jwt_required()
def changePasswordView():
    passwordDetails = request.get_json()
    outcomeMessage, statusCode = changePassword(current_user, passwordDetails)
    return json.dumps(outcomeMessage), statusCode

#Creates a PUT route to facilitate the change of a password of an existing user. Also returns a status code to denote the outcome of the operation.
@userViews.route('/user/profile', methods=["PUT"])
@jwt_required()
def changeNameView():
    profileDetails = request.get_json()
    outcomeMessage, statusCode = updateProfile(current_user, profileDetails)
    return json.dumps(outcomeMessage), statusCode


#Creates a GET route to return the details of the current user. Also returns a status code to denote the outcome of the operation.
@userViews.route("/identify", methods=["GET"])
#Ensures that this route is only accessible to logged in users.
@jwt_required()
def identify():
    outcomeMessage, statusCode = identifyUser(current_user)
    return json.dumps(outcomeMessage), statusCode


#Creates a PUT route to facilitate the confirmation of the user's account. Also returns a status code to denote the outcome of the operation.
@userViews.route('/confirm/<token>', methods=["PUT"])
def confirmEmail(token):
    details = request.get_json()
    outcomeMessage, statusCode = confirmEmailController(token, details)
    return json.dumps(outcomeMessage), statusCode

#Creates a POST route to facilitate the resending of the confirmation email for a user's account. Also returns a status code to denote the outcome of the operation.
@userViews.route('/resendConfirmation', methods=["POST"])
def resendConfirmation():
    details = request.get_json()
    outcomeMessage, statusCode = resendConfirmationController(details)
    return json.dumps(outcomeMessage), statusCode

#Creates a POST route to facilitate the resending of the password reset email for a user's account. Also returns a status code to denote the outcome of the operation.
@userViews.route('/resetPassword', methods=["POST"])
def sendPasswordReset():
    details = request.get_json()
    outcomeMessage, statusCode = sendPasswordResetController(details)
    return json.dumps(outcomeMessage), statusCode

#Creates a POST route to facilitate the resetting of a user's password. Also returns a status code to denote the outcome of the operation.
@userViews.route('/resetPassword/<token>', methods=["POST"])
def resetPassword(token):
    details = request.get_json()
    outcomeMessage, statusCode = resetPasswordController(details, token)
    return json.dumps(outcomeMessage), statusCode