#Justin Baldeosingh
#SpotDPothole-Backend
#NULLIFY

#USER CONTROLLERS - Facilitate interactions between the user model and the other models/controllers of the application.

#Imports flask modules and json.
from flask_jwt_extended import create_access_token, jwt_required
from flask import session
from flask_mail import Mail, Message
from sqlalchemy.exc import IntegrityError, OperationalError
import json
import bleach

#Imports the all of the required models and controllers.
from App.models import *
from App.controllers import *
from App.controllers.report import reportPotholeDriver, reportPotholeStandard
from ..token import confirm_token, generate_confirmation_token

mail = Mail()

#Facilitates the registration of a user in the application given a dictionary containing registration information.
#The appropriate outcome and status codes are then returned.
def registerUserController(regData):  
    #Attempts to register the user using the registration data.
    try:
        #If the registration data is not null, process the data.
        if regData:
            #Ensures that all of the fields for registration are contained in the dictionary.
            if "email" in regData and "firstName" in regData and "lastName" in regData and "password" in regData and "confirmPassword" in regData and "agreeToS" in regData:
                #Parses the emails, first names and last names to ensure that there are no padded spaces.
                parsedEmail = regData["email"].replace(" ", "")
                parsedFirstName = regData["firstName"].replace(" ", "")
                parsedLastName = regData["lastName"].replace(" ", "")

                #Ensures the user has agreed to the terms of service, and returns an appropriate error and status code if otherwise.
                if regData["agreeToS"] != True:
                    return {"error" : "User did not agree to terms of service."}, 400

                #Ensures the user has entered a valid email, and returns an appropriate error and status code if otherwise.
                if len(parsedEmail) < 3 or not "@" in parsedEmail or not "." in parsedEmail:
                    return {"error" : "Email is invalid!"}, 400

                #Ensures the user has entered a valid first name, and returns an appropriate error and status code if otherwise.
                if len(parsedFirstName) < 2:
                    return {"error" : "First name is invalid!"}, 400
                
                #Ensures the user has entered a valid last name, and returns an appropriate error and status code if otherwise.
                if len(parsedLastName) < 2:
                    return {"error": "Last name is invalid!"}, 400

                #Ensures the user has entered a long enough password, and returns an appropriate error and status code if otherwise.
                if len(regData["password"]) < 6:
                    return {"error": "Password is too short"}, 400
                
                #Ensures the user has entered matching passwords, and returns an appropriate error and status code if otherwise.
                if regData["password"] != regData["confirmPassword"]:
                    return {"error" : "Passwords do not match!"}, 400

                #Attempts to register the user by adding them to the database.
                try:
                    #Creates a new user object using the parsed registration data.
                    newUser = User(parsedEmail, parsedFirstName, parsedLastName, regData["password"])
                    #Adds and commits the user to the database, and returns a success message and 'CREATED' http status code (201).
                    db.session.add(newUser)
                    db.session.commit()

                    token = generate_confirmation_token(newUser.email)
                    print(token)

                    subject = "SpotDPothole - Please confirm your email"
                    
                    msg = Message(
                        subject = "SpotDPothole - Please confirm your email",
                        recipients=[newUser.email], 
                        body = f"Please use the following confirmation token: {token}",
                        sender = "spotdpothole-email-confirmation@justinbaldeo.com"
                    )

                    #mail.send(msg)

                    return {"message" : "Sucesssfully registered!"}, 201
                #If an integrity error exception is generated, there would already exist a user with the same email in the database.
                except IntegrityError:
                    #Rollback the database and return an error message and a 'CONFLICT' http status code (409)
                    db.session.rollback()
                    return {"error" : "User already exists!"}, 409
                #If an operational error exception is generated, the database would not be initialized to handle the request.
                except OperationalError:
                    #Print a message to the application console and notify the user that there was an error via an error message response.
                    #Returns a "INTERNAL SERVER ERROR" http status code (500).
                    print("Database not initialized!")
                    return {"error" : "Database not initialized! Contact the administrator of the application!"}, 500
                #Otherwise, return an error message stating that an unknown error has occured and a 'INTERNAL SERVER ERROR' http status code (500).
                except:
                    #Rollback the database
                    db.session.rollback()
                    return {"error" : "An unknown error has occurred!"}, 500
                    

        #If the registration data is null, return an error message along with a 'BAD REQUEST' http status code (400).    
        db.session.rollback()    
        return {"error" : "Invalid registration details provided!"}, 400
    except:
    #If registering the user fails (Due to invalid data types being used), rollback the database and return an error.
        db.session.rollback()
        return {"error" : "Unable to register with user details!"}, 400

#Facilitates the login of a user in the application given a dictionary containing login information.
#The appropriate outcome and status codes are then returned.
def loginUserController(loginDetails): 
    #Attempts to login the user with their login details. 
    try:
        #If the login data is not null, process the data.
        if loginDetails:
            #Ensures that all of the fields for login are contained in the dictionary.
            if "email" in loginDetails and "password" in loginDetails:
                #Finds and stores the user account object for the associated email, within the database.
                userAccount = User.query.filter_by(email=loginDetails["email"]).first()

                #If the account does not exist or the password is invalid, return an error stating that the wrong details were entered.
                #Also return a "UNAUTHORIZED" http status code (401).
                if not userAccount or not userAccount.checkPassword(loginDetails["password"]):
                    return {"error" : "Wrong email or password entered!"}, 401

                if userAccount.banned:
                    return {"error": "User is banned."}, 403

                if not userAccount.confirmed:
                    return {"error": "Please confirm your account before proceeding. Check your email for a verification link."}, 403

                #If the login credentials are verified, create an access token for the user's session.
                #The access token would then be returned along with an 'OK' http status code (200).
                if userAccount and userAccount.checkPassword(loginDetails["password"]):
                    access_token = create_access_token(identity = loginDetails["email"])
                    if loginDetails["email"].find("tester") == -1:
                        session.permanent = True
                    return {"access_token" : access_token}, 200

        #If the login data is null, return an error message along with an 'UNAUTHORIZED' http status code (401).   
        db.session.rollback()
        return {"error" : "Invalid login details provided!"}, 401
    except:
    #If the login details are composed using invalid datatypes, the query for the user object will fail and there will be no rollback to recover.
        #Rollback recovers the error in the event of invalid data in the login request. Also returns an error.
        db.session.rollback()
        return {"error" : "Unable to login with user details!"}, 400

#Changes the password of the current user to match the new password details
def changePassword(current_user, newPasswordDetails):
    try:
        if newPasswordDetails:
            if "oldPassword" in newPasswordDetails and "password" in newPasswordDetails and "confirmPassword" in newPasswordDetails:
                if not current_user.checkPassword(newPasswordDetails["oldPassword"]):
                    return {"error" : "The original password you have entered is incorrect!"}, 400

                if newPasswordDetails["password"] != newPasswordDetails["confirmPassword"]:
                    return {"error" : "Passwords do not match!"}, 400

                if len(newPasswordDetails["password"]) < 6:
                    return {"error" : "Password is too short!"}, 400

                try:
                    current_user.setPassword(newPasswordDetails["password"])
                    db.session.add(current_user)
                    db.session.commit()
                    return {"message" : "Sucesssfully changed password!"}, 200
                except:
                    return {"error" : "An unknown error has occurred!"}, 500

        return {"error" : "Invalid password details supplied!"}, 400
    except:
        db.session.rollback()
        return {"error" : "You are not logged in!"}, 400


#Changes the password of the current user to match the new password details
def updateProfile(current_user, profileDetails):
    if profileDetails:
        if "firstName" in profileDetails and "lastName" in profileDetails:
            parsedFirstName = profileDetails["firstName"].replace(" ", "")
            parsedLastName = profileDetails["lastName"].replace(" ", "")

            if len(parsedFirstName) < 2:
                return {"error" : "First name is too short!"}, 400

            if len(parsedLastName) < 2:
                return {"error" : "Last name is too short!"}, 400

            try:
                current_user.firstName = parsedFirstName
                current_user.lastName = parsedLastName

                db.session.add(current_user)
                db.session.commit()
                return {"message" : "Sucesssfully updated profile!"}, 200
            except:
                return {"error" : "An unknown error has occurred!"}, 500

    return {"error" : "Invalid profile details supplied!"}, 400


#Returns the user's information given a user object.
def identifyUser(current_user):
    #Attempts to indentify a user given their JWT identified user object.
    try:
        #If the user object is not null, return the details for the user object.
        if current_user:
            return {"userID" : current_user.userID, "email" : bleach.clean(current_user.email), "firstName" : bleach.clean(current_user.firstName), "lastName": bleach.clean(current_user.lastName), "confirmed": current_user.confirmed}, 200
        #Otherwise, return an error message and an 'UNAUTHORIZED' http status code (401).
        return {"error" : "User is not logged in!"}, 401
    except:
    #If identifying the user fails, rollback the database.
        db.session.rollback()
        return {"error" : "Unable to identify user!"}, 400

########### SYSTEM CONTROLLERS ###########
#Used for banning a user given their email.
def banUserController(email):
    try:
        foundUser = db.session.query(User).filter_by(email=email).first()
        if(foundUser):
            try:
                foundUser.banned = True
                db.session.add(foundUser)
                db.session.commit()
            except:
                print("Unable to ban user!")
        else:
            print("No user found with that email!")
    except:
        db.session.rollback()
        print("Unable to ban user!")

#User for unbanning a user given their email.
def unbanUserController(email):
    try:
        foundUser = db.session.query(User).filter_by(email=email).first()
        if(foundUser):
            try:
                foundUser.banned = False
                db.session.add(foundUser)
                db.session.commit()
            except:
                print("Unable to ban user!")
        else:
            print("No user found with that email!")
    except:
        db.session.rollback()
        print("Unable to ban user!")

def confirmEmailController(token):
    try:
        try:
            email = confirm_token(token)
        except:
            return {"error" : "Confirmation link is invalid or has expired!"}, 400
        
        user = User.query.filter_by(email=email).first_or_404()
        print(user)
        if user.confirmed:
            return {"message" : "User already confirmed!"}, 200
        else:
            user.confirmed = True
            db.session.add(user)
            db.session.commit()
            return {"message" : "User has been confirmed. You may now login."}, 200
    except:
        db.session.rollback()
        return {"error" : "Confirmation link is invalid or has expired!"}, 400

def resendConfirmationController(details):
    try:
        if details:
            if "email" in details:
                email = details["email"]
                token = generate_confirmation_token(email)

                subject = "SpotDPothole - Please confirm your email"

                msg = Message(
                    subject = "SpotDPothole - Please confirm your email",
                    recipients=[email], 
                    body = f"Please use the following confirmation token: {token}",
                    sender = "spotdpothole-email-confirmation@justinbaldeo.com"
                )

                mail.send(msg)

                return {"message": "Confirmation remail resent!"}, 200
            else:
                return {"error": "Invalid email provided!"}, 400
        else:
            return {"error": "Invalid email provided!"}, 400
    except:
        db.session.rollback()
        return {"error": "Unable to send confirmation link!"}, 400


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