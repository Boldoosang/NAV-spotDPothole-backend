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

##### CHANGE TESTCONFIRMED TO FALSE WHEN FULLY DEPLOYING TO AVOID EMAIL CONFIRMATION #########
def registerUserController(regData, testConfirmed=True, testing=False):  
    validDomains = ["gmail.com", "yahoo.com", "hotmail.com", "my.uwi.edu", "outlook.com"]
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

                domain = parsedEmail.split('@')[1]
                if domain not in validDomains:
                    return {"error" : "Please use gmail, yahoo, hotmail, outlook, or my.uwi.edu email providers."}, 400

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
                    newUser = User(parsedEmail, parsedFirstName, parsedLastName, regData["password"], confirmed=testConfirmed)
                    #Adds and commits the user to the database, and returns a success message and 'CREATED' http status code (201).
                    db.session.add(newUser)
                    db.session.commit()

                    token = generate_confirmation_token(newUser.email)

                    if not testConfirmed:
                        msg = Message(
                            subject = "SpotDPothole - Please confirm your email",
                            recipients=[newUser.email], 
                            body = f"Please use the following confirmation token: {token}",
                            sender = "spotdpothole-email-confirmation@justinbaldeo.com"
                        )

                        if not testing:
                            mail.send(msg)

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
                except Exception as e:
                    print(e)
                    #Rollback the database
                    db.session.rollback()
                    return {"error" : "An unknown error has occurred! (H)"}, 500
                    

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
                    db.session.rollback()
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

def confirmEmailController(token, details):
    try:
        try:
            if "email" in details:
                activeUser = user = User.query.filter_by(email=details["email"]).first()

                if not activeUser:
                    return {"error" : "Email address not registered!"}, 400
        except Exception as e:
            print(e)
            return {"error" : "Email address not provided!"}, 400

        try:
            email = confirm_token(token)
        except:
            return {"error" : "Confirmation token is invalid or has expired!"}, 400

        if email != details["email"]:
            return {"error" : "Token is not associated with this email address or is invalid!"}, 400
        
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
        return {"error" : "Confirmation token is invalid or has expired!"}, 400

def resendConfirmationController(details, testing=False):
    try:
        if details:
            if "email" in details:
                email = details["email"]
                
                activeUser = user = User.query.filter_by(email=email, confirmed=False).first()

                if not activeUser:
                    return {"error" : "Email address not registered or user already confirmed!"}, 400


                token = generate_confirmation_token(email)

                msg = Message(
                    subject = "SpotDPothole - Please confirm your email",
                    recipients=[email], 
                    body = f"Please use the following confirmation token: {token}",
                    sender = "spotdpothole-email-confirmation@justinbaldeo.com"
                )

                if not testing:
                    mail.send(msg)

                return {"message": "Confirmation email resent!"}, 200
            else:
                return {"error": "Invalid email provided!"}, 400
        else:
            return {"error": "Invalid email provided!"}, 400
    except:
        db.session.rollback()
        return {"error": "Unable to send confirmation token!"}, 400


def sendPasswordResetController(details, testing=False):
    try:
        if details:
            if "email" in details:
                email = details["email"]

                try:
                    user = db.session.query(User).filter_by(email=email).first()
                    if user == None:
                        return {"error": "Unregistered email provided!"}, 404
                except:
                    db.session.rollback()
                    return {"error": "Invalid email provided!"}, 400

                token = generate_confirmation_token(email)

                msg = Message(
                    subject = "SpotDPothole - Please reset your password",
                    recipients=[email], 
                    body = f"Please use the following confirmation token: {token}",
                    sender = "spotdpothole-email-confirmation@justinbaldeo.com"
                )

                if not testing:
                    mail.send(msg)

                return {"message": "Password reset email resent!"}, 200
            else:
                return {"error": "Invalid email provided!"}, 400
        else:
            return {"error": "Invalid email provided!"}, 400
    except:
        db.session.rollback()
        return {"error": "Unable to send reset email!"}, 400

def resetPasswordController(details, token):
    try:
        if details:
            try:
                if "email" in details:
                    activeUser = user = User.query.filter_by(email=details["email"]).first()

                    if not activeUser:
                        return {"error" : "Email address not registered!"}, 404
            except:
                return {"error" : "Email address not provided!"}, 400
            

            try:
                email = confirm_token(token)
            except:
                return {"error" : "Confirmation token is invalid or has expired!"}, 400
            
            if email != details["email"]:
                return {"error" : "Token is not associated with this email address or is invalid!"}, 400

            user = User.query.filter_by(email=email).first_or_404()


            if "password" in details and "confirmPassword" in details:
                if details["password"] != details["confirmPassword"]:
                    return {"error" : "Passwords do not match!"}, 400

                if len(details["password"]) < 6:
                    return {"error" : "Password is too short!"}, 400

                try:
                    user.setPassword(details["password"])
                    db.session.add(user)
                    db.session.commit()
                    return {"message" : "Sucesssfully reset password!"}, 200
                except:
                    db.session.rollback()
                    return {"error" : "An unknown error has occurred!"}, 500


        else:
            return {"error" : "No updated password details provided!"}, 400
    except:
        db.session.rollback()
        return {"error" : "Confirmation token is invalid or has expired!"}, 400






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
    }, True)
    registerUserController({
        "email" : "tester2@yahoo.com",
        "firstName" : "Jose",
        "lastName" : "Kerron",
        "password" : "121233",
        "confirmPassword" : "121233",
        "agreeToS": True
    }, True)
    registerUserController({
        "email" : "tester3@yahoo.com",
        "firstName" : "Mary",
        "lastName" : "Hamilton",
        "password" : "121233",
        "confirmPassword" : "121233",
        "agreeToS": True
    }, True)
    registerUserController({
        "email" : "tester4@yahoo.com",
        "firstName" : "Keisha",
        "lastName" : "Dan",
        "password" : "121233",
        "confirmPassword" : "121233",
        "agreeToS": True
    }, True)
    registerUserController({
        "email" : "tester5@yahoo.com",
        "firstName" : "Harry",
        "lastName" : "Potter",
        "password" : "121233",
        "confirmPassword" : "121233",
        "agreeToS": True
    }, True)
    registerUserController({
        "email" : "tester6@yahoo.com",
        "firstName" : "Terrence",
        "lastName" : "Williams",
        "password" : "121233",
        "confirmPassword" : "121233",
        "agreeToS": True
    }, True)

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
    data = open("App/tests/testImage.txt", "r").read()

    reportDetails1 = {
        "longitude" : -61.277001,
        "latitude" : 10.726551,
        "constituencyID" : "arima",
        "description": "Very large pothole spanning both lanes of the road.",
        "images" : [
            data
        ]
    }

    reportDetails2 = {
        "longitude" : -61.395376,
        "latitude" : 10.511998,
        "constituencyID" : "chaguanas",
        "description": "Small pothole in center of road",
        "images" : [
            data
        ]
    }

    reportDetails3 = {
        "longitude" : -61.400837,
        "latitude" : 10.502230,
        "constituencyID" : "chaguanas",
        "description": "Very large pothole.",
        "images" : [
            data
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



    reportPotholeStandard(user1, reportDetails1, Testing=True)
    reportPotholeStandard(user2, reportDetails2, Testing=True)
    reportPotholeStandard(user3, reportDetails3, Testing=True)   
    reportPotholeDriver(user4, reportDetails4)
    reportPotholeDriver(user5, reportDetails5)
    reportPotholeDriver(user6, reportDetails6)