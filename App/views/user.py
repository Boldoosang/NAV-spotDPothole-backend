#Justin Baldeosingh
#SpotDPothole-Backend
#NULLIFY

#USER VIEW - Defines the view endpoints for REPORTEDIMAGES.

#Imports flask modules.
from flask_jwt_extended import jwt_required, current_user
from flask import Blueprint, request, jsonify, send_from_directory, url_for, redirect
# decorator for routes that should be accessible only by logged in users
from .auth_decorator import login_required
from .oauth import oauth

#Creates a blueprint to the collection of views for users.
userViews = Blueprint('userViews', __name__)

#Imports the all of the controllers of the application.
from App.controllers import *
from App.controllers.user import identifyUser, processGoogleUserController



#Creates a GET route to return the details of the current user. Also returns a status code to denote the outcome of the operation.
@userViews.route("/identify", methods=["GET"])
#Ensures that this route is only accessible to logged in users.
@login_required
def identify():
    outcomeMessage, statusCode = identifyUser(session["profile"])
    return json.dumps(outcomeMessage), statusCode


    

@userViews.route('/')
@login_required
def hello_world():
    return (session)


@userViews.route('/login')
def login():
    google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('userViews.authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@userViews.route('/authorize')
def authorize():
    try:
        google = oauth.create_client('google')  # create the google oauth client
        token = google.authorize_access_token()  # Access token from google (needed to get user info)
        resp = google.get('userinfo')  # userinfo contains stuff u specificed in the scrope
        user_info = resp.json()
        user = oauth.google.userinfo()
        session['profile'] = user_info
        session.permanent = True  # make the session permanant so it keeps existing after browser gets closed

        resp = processGoogleUserController(session["profile"])
        print(resp)

        return redirect('/')
    except:
        return {"error" : "You do not have permission to access this route. Use the login to authorize yourself into the application."}, 403
    


@userViews.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')


