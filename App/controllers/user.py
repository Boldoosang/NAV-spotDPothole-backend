#Justin Baldeosingh
#SpotDPothole-Backend
#NULLIFY

#USER CONTROLLERS - Facilitate interactions between the user model and the other models/controllers of the application.

#Imports flask modules and json.
from flask_jwt_extended import create_access_token, jwt_required
from flask import session
from sqlalchemy.exc import IntegrityError, OperationalError
import json
import bleach

#Imports the all of the required models and controllers.
from App.models import *
from App.controllers import *
from App.controllers.report import reportPotholeDriver, reportPotholeStandard

#Facilitates the registration of a user in the application given a dictionary containing registration information.
#The appropriate outcome and status codes are then returned.
def processGoogleUserController(userData):  
    #Attempts to register the user using the registration data.
    try:
        #If the registration data is not null, process the data.
        if userData:
            try:
                foundUser = db.session.query(User).filter_by(googleID=userData["id"]).one_or_none()            

                if foundUser == None:
                    try:
                        newUser = User(googleID = userData["id"], email = userData["email"], firstName = userData["given_name"], lastName = userData["family_name"], banned = 0, picture = userData["picture"])
                        #Adds and commits the user to the database, and returns a success message and 'CREATED' http status code (201).
                        db.session.add(newUser)
                        db.session.commit()
                        return {"message" : "Sucesssfully registered!"}, 201
                    except Exception as e:
                        return {"error" : "Unable to create new user!"}, 500
                else:
                    return {"message" : "Sucesssfully logged in as successful user!"}, 200

            except:
                #If registering the user fails (Due to invalid data types being used), rollback the database and return an error.
                db.session.rollback()
                return {"error" : "Unable to load user!"}, 500

        else:
            #If registering the user fails (Due to invalid data types being used), rollback the database and return an error.
            db.session.rollback()
            return {"error" : "No user data provided!"}, 400
    except:
    #If registering the user fails (Due to invalid data types being used), rollback the database and return an error.
        db.session.rollback()
        return {"error" : "Unable to process user with user details!"}, 400


#Returns the user's information given a user object.
def identifyUser(session):
    try:
        current_user = loadUser(session)

        if current_user:
            return {"userID" : current_user.userID, "email" : bleach.clean(current_user.email), "firstName" : bleach.clean(current_user.firstName), "lastName": bleach.clean(current_user.lastName), "picture" : current_user.picture}, 200

        return {"error" : "User is not logged in!"}, 401
    except:
        return {"error" : "Unable to identify user!"}, 500


def loadUser(session):
    try:
        foundUser = db.session.query(User).filter_by(googleID=session["id"]).one_or_none()  
        return foundUser
    except:
        db.session.rollback()
        return None

##################### TEST CONTROLLERS #####################
#Creates test users for fixtures.
def createTestUsers():
    registerUserController({
        "email" : "tester1@yahoo.com",
        "firstName" : "Moses",
        "lastName" : "Darren",
        "password" : "121233",
        "confirmPassword" : "121233",
        "agreeToS": True
    })
    registerUserController({
        "email" : "tester2@yahoo.com",
        "firstName" : "Jose",
        "lastName" : "Kerron",
        "password" : "121233",
        "confirmPassword" : "121233",
        "agreeToS": True
    })
    registerUserController({
        "email" : "tester3@yahoo.com",
        "firstName" : "Mary",
        "lastName" : "Hamilton",
        "password" : "121233",
        "confirmPassword" : "121233",
        "agreeToS": True
    })
    registerUserController({
        "email" : "tester4@yahoo.com",
        "firstName" : "Keisha",
        "lastName" : "Dan",
        "password" : "121233",
        "confirmPassword" : "121233",
        "agreeToS": True
    })
    registerUserController({
        "email" : "tester5@yahoo.com",
        "firstName" : "Harry",
        "lastName" : "Potter",
        "password" : "121233",
        "confirmPassword" : "121233",
        "agreeToS": True
    })
    registerUserController({
        "email" : "tester6@yahoo.com",
        "firstName" : "Terrence",
        "lastName" : "Williams",
        "password" : "121233",
        "confirmPassword" : "121233",
        "agreeToS": True
    })

#Returns all registered users in the database.
def getAllRegisteredUsers():
    allUsers = User.query.all()
    return json.dumps([u.toDict() for u in allUsers])

#Returns one of the registered users in the database given their email.
def getOneRegisteredUser(email):
    testUser = db.session.query(User).filter_by(email=email).first()
    return testUser

#Creates simulated report data, simulated users, and has those simulated users file those simulated reports.
def createSimulatedData():
    createTestUsers()

    reportDetails1 = {
        "longitude" : -61.277001,
        "latitude" : 10.726551,
        "constituencyID" : "arima",
        "description": "Very large pothole spanning both lanes of the road.",
        "images" : [
            "https://www.howtogeek.com/wp-content/uploads/2018/08/Header.png"
        ]
    }

    reportDetails2 = {
        "longitude" : -61.395376,
        "latitude" : 10.511998,
        "constituencyID" : "chaguanas",
        "description": "Small pothole in center of road",
        "images" : [
            "https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885__480.jpg"
        ]
    }

    reportDetails3 = {
        "longitude" : -61.400837,
        "latitude" : 10.502230,
        "constituencyID" : "chaguanas",
        "description": "Very large pothole.",
        "images" : [
            "https://images.unsplash.com/photo-1541963463532-d68292c34b19?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxleHBsb3JlLWZlZWR8Mnx8fGVufDB8fHx8&w=1000&q=80"
        ]
    }

    reportDetails4 = {
        "longitude" : -61.277000,
        "latitude" : 10.726550,
        "constituencyID" : "arima",
    }

    reportDetails5 = {
        "longitude" : -61.452443,
        "latitude" : 10.650744,
        "constituencyID" : "san_juan",
    }

    reportDetails6 = {
        "longitude" : -61.466627,
        "latitude" : 10.648361,
        "constituencyID" : "san_juan",
    }

    user1 = getOneRegisteredUser("tester1@yahoo.com")
    user2 = getOneRegisteredUser("tester2@yahoo.com")
    user3 = getOneRegisteredUser("tester3@yahoo.com")
    user4 = getOneRegisteredUser("tester4@yahoo.com")
    user5 = getOneRegisteredUser("tester5@yahoo.com")
    user6 = getOneRegisteredUser("tester6@yahoo.com")



    reportPotholeStandard(user1, reportDetails1)
    reportPotholeStandard(user2, reportDetails2)
    reportPotholeStandard(user3, reportDetails3)   
    reportPotholeDriver(user4, reportDetails4)
    reportPotholeDriver(user5, reportDetails5)
    reportPotholeDriver(user6, reportDetails6)