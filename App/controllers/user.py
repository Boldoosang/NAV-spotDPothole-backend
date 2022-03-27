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

#Imports functions for confirming and generating tokens.
from ..token import confirm_token, generate_confirmation_token

#Declares the main mail object.
mail = Mail()

#Facilitates the registration of a user in the application given a dictionary containing registration information.
#The appropriate outcome and status codes are then returned.

##### CHANGE TESTCONFIRMED TO FALSE WHEN FULLY DEPLOYING TO AVOID EMAIL CONFIRMATION #########
def registerUserController(regData, testConfirmed=True, testing=False):  
    #Sets the valid email provider domains for registration.
    validDomains = ["gmail.com", "yahoo.com", "hotmail.com", "my.uwi.edu", "sta.uwi.edu", "outlook.com"]
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

                    #Generates a confirmation token for the new user's email address.
                    token = generate_confirmation_token(newUser.email)

                    #If the user is not confirmed by default (testing), create and send a confirmation email to the email address.
                    if not testConfirmed:
                        msg = Message(
                            subject = "SpotDPothole - Please confirm your email",
                            recipients=[newUser.email], 
                            body = f"Please use the following confirmation token: {token}",
                            sender = "spotdpothole-email-confirmation@justinbaldeo.com"
                        )

                        #If the app is not being tested, send the email.
                        if not testing:
                            mail.send(msg)

                    #Returns the a success message and status code.
                    return {"message" : "Successfully registered! Please check your email for your confirmation token!"}, 201
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
                    #Prints the exception for registration.
                    print(e)
                    #Rollback the database
                    db.session.rollback()
                    return {"error" : "An unknown error has occurred! (Heroku)"}, 500
                    

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

                #If the user is banned, return an error and do not let them login.
                if userAccount.banned:
                    return {"error": "User is banned."}, 403

                #If the user is not confirmed, return an error and do not let them login.
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
    #Attempts to change the user's password with the new password details. 
    try:
        #Ensures that the request contains the password details.
        if newPasswordDetails:
            #Ensures that the password details has all of the required fields for changing the passwords.
            if "oldPassword" in newPasswordDetails and "password" in newPasswordDetails and "confirmPassword" in newPasswordDetails:
                #Ensures that the original password matches the correct password of the user.
                if not current_user.checkPassword(newPasswordDetails["oldPassword"]):
                    return {"error" : "The original password you have entered is incorrect!"}, 400

                #Ensures that both password and confirmed passwords are the same.
                if newPasswordDetails["password"] != newPasswordDetails["confirmPassword"]:
                    return {"error" : "Passwords do not match!"}, 400

                #Ensures that the password has a minimum length of 6.
                if len(newPasswordDetails["password"]) < 6:
                    return {"error" : "Password is too short!"}, 400

                #Sets the password of the user to the new password.
                try:
                    current_user.setPassword(newPasswordDetails["password"])
                    db.session.add(current_user)
                    db.session.commit()
                    return {"message" : "Successfully changed password!"}, 200
                except:
                #Otherwise, an unknown error has occurred.
                    db.session.rollback()
                    return {"error" : "An unknown error has occurred!"}, 500
        #If not newPasswordDetails are provided, return an error.
        return {"error" : "Invalid password details supplied!"}, 400
    except:
    #If failing to change the password, rollback the database and return a not logged in error.
        db.session.rollback()
        return {"error" : "You are not logged in!"}, 400


#Changes the name of the current user to match the new name details
def updateProfile(current_user, profileDetails):
    #Ensures that the profileDetails provided is not null.
    if profileDetails:
        #Ensures that the profileDetails contains the firstName and lastName fields.
        if "firstName" in profileDetails and "lastName" in profileDetails:
            #Parses the names.
            parsedFirstName = profileDetails["firstName"].replace(" ", "")
            parsedLastName = profileDetails["lastName"].replace(" ", "")

            #Ensures that the firstName is not too short.
            if len(parsedFirstName) < 2:
                return {"error" : "First name is too short!"}, 400

            #Ensures that the lastName is not too short.
            if len(parsedLastName) < 2:
                return {"error" : "Last name is too short!"}, 400

            #Attempts to update the first name and last name of the current user.
            try:
                current_user.firstName = parsedFirstName
                current_user.lastName = parsedLastName

                db.session.add(current_user)
                db.session.commit()

                #Returns a success message outcome and status code.
                return {"message" : "Successfully updated profile!"}, 200
            except:
                #Rollback the database and return an error message outcome and status code.
                db.session.rollback()
                return {"error" : "An unknown error has occurred!"}, 500

    #Otherwise if no profile details are provided, return an error message and status code.
    return {"error" : "Invalid profile details supplied!"}, 400


#Returns the user's information given a user object.
def identifyUser(current_user):
    #Attempts to indentify a user given their JWT identified user object.
    try:
        #If the user object is not null, return the details for the user object.
        if current_user:
            #Returns a bleached version of the data such that the input is sanitized.
            return {"userID" : current_user.userID, "email" : bleach.clean(current_user.email), "firstName" : bleach.clean(current_user.firstName), "lastName": bleach.clean(current_user.lastName), "confirmed": current_user.confirmed}, 200
        #Otherwise, return an error message and an 'UNAUTHORIZED' http status code (401).
        return {"error" : "User is not logged in!"}, 401
    except:
    #If identifying the user fails, rollback the database.
        db.session.rollback()
        return {"error" : "Unable to identify user!"}, 400

#Confirms a user's account given their email and token.
def confirmEmailController(token, details):
    #Attempts to confirm the user's email.
    try:
        #Attempts to parse the email address and retrieve the user.
        try:
            #Ensurse that the details contains an email field.
            if "email" in details:
                #Finds the user with the email address.
                activeUser = user = User.query.filter_by(email=details["email"]).first()

                #If no user is found, return an error that the email address is not registered.
                if not activeUser:
                    return {"error" : "Email address not registered!"}, 400
        except Exception as e:
        #Otherwise, the email field cannot be parsed as no value was provided.
            print(e)
            return {"error" : "Email address not provided!"}, 400

        #Attempts to obtain the email address assigned to the token.
        try:
            email = confirm_token(token)
        except:
        #If no email address could be obtained, return an invalid token error.
            return {"error" : "Confirmation token is invalid or has expired!"}, 400

        #If the email address of the token does not match the email address being confirmed, return an error.
        if email != details["email"]:
            return {"error" : "Token is not associated with this email address or is invalid!"}, 400
        
        #Gets a handle on the user that corresponds to the email address associated with the token.
        user = User.query.filter_by(email=email).first_or_404()
        #If the user has already been confirmed, return a success message and status code.
        if user.confirmed:
            return {"message" : "User already confirmed!"}, 200
        else:
        #Otherwise, update the confirmed status of the user and return a success message and status code.
            user.confirmed = True
            db.session.add(user)
            db.session.commit()
            return {"message" : "User has been confirmed. You may now login."}, 200
    except:
    #Otherwise, the request could not be parsed for the given token. Rollback the database and return an error.
        db.session.rollback()
        return {"error" : "Confirmation token is invalid or has expired!"}, 400

#Resends a confirmation email to the user.
def resendConfirmationController(details, testing=False):
    #Attempts to find the user, generate and send the email to the user.
    try:
        #If the request contains details, process the request.
        if details:
            #Ensures that the details has a email field.
            if "email" in details:
                email = details["email"]
                
                #Finds a user the corresponds to the email and is not already confirmed.
                activeUser = user = User.query.filter_by(email=email, confirmed=False).first()

                #If no user can be found, return an error that the email may not be registered or the user is confirmed.
                if not activeUser:
                    return {"error" : "Email address not registered or user already confirmed!"}, 400

                #Generates a corresponding token for the user's email address.
                token = generate_confirmation_token(email)

                #Creates the email message to be sent to the email address.
                msg = Message(
                    subject = "SpotDPothole - Please confirm your email",
                    recipients=[email], 
                    body = f"Please use the following confirmation token: {token}",
                    sender = "spotdpothole-email-confirmation@justinbaldeo.com"
                )

                #If the backend is not in testing mode, send the email.
                if not testing:
                    mail.send(msg)

                #Send a success message and status code.
                return {"message": "Confirmation email resent!"}, 200
            else:
            #Otherwise, return an error that the email was not provided.
                return {"error": "Invalid email provided!"}, 400
        else:
        #Otherwise, return an error that the details object containing the email was not provided.
            return {"error": "Invalid email provided!"}, 400
    except:
    #Otherwise, an unknown error has occured. Rollback the database and send an error message and code.
        db.session.rollback()
        return {"error": "Unable to send confirmation token!"}, 400

#Sends a password reset email to the user.
def sendPasswordResetController(details, testing=False):
    #Attempts to find the user, generate and send the email to the user.
    try:
        #If the request contains details, process the request.
        if details:
            #Ensures that the details has a email field.
            if "email" in details:
                email = details["email"]

                #Determines if a user exists with the provided email.
                try:
                    user = db.session.query(User).filter_by(email=email).first()
                    if user == None:
                        return {"error": "Unregistered email provided!"}, 404
                except:
                #Otherwise, notify the user that an invalid email has been provided.
                    db.session.rollback()
                    return {"error": "Invalid email provided!"}, 400

                #Generates a token for the email address.
                token = generate_confirmation_token(email)

                #Creates the email message containing the token.
                msg = Message(
                    subject = "SpotDPothole - Please reset your password",
                    recipients=[email], 
                    body = f"Please use the following confirmation token: {token}",
                    sender = "spotdpothole-email-confirmation@justinbaldeo.com"
                )

                #If not in testing mode, send the email with the token to the user.
                if not testing:
                    mail.send(msg)

                #Notify the user that the email has been sent.
                return {"message": "Password reset email resent!"}, 200
            else:
            #Otherwise, an invalid email address has been provided.
                return {"error": "Invalid email provided!"}, 400
        else:
        #Otherwise, no email field was contained in the details object.
            return {"error": "Invalid email provided!"}, 400
    except:
    #Otherwise, rollback the database if an unknown error has occurred and inform the user.
        db.session.rollback()
        return {"error": "Unable to send reset email!"}, 400

#Facilitates the resetting of the password of a user given their email, password details, and token.
def resetPasswordController(details, token):
    #Attempts to reset the password of the user.
    try:
        #If the request contains details, process the request.
        if details:
            #Ensures that the current user is an active user of the system.
            try:
                #Ensures that the details has a email field.
                if "email" in details:
                    activeUser = user = User.query.filter_by(email=details["email"]).first()

                    #If the user is not an active user, then the email is not registered; return a message outcome.
                    if not activeUser:
                        return {"error" : "Email address not registered!"}, 404
            except:
            #Otherwise, no email was provided.
                return {"error" : "Email address not provided!"}, 400
            
            #Attempts to obtain the email address associated with the token.
            try:
                email = confirm_token(token)
            except:
            #Otherwise, no email could be obtained for that token; return an error.
                return {"error" : "Confirmation token is invalid or has expired!"}, 400
            
            #If the email obtained does not match the email of the request, return an error that the token does not match the account.
            if email != details["email"]:
                return {"error" : "Token is not associated with this email address or is invalid!"}, 400

            #Obtains the user object associated with the email.
            user = User.query.filter_by(email=email).first_or_404()

            #Ensures that the required fields are in the details object.
            if "password" in details and "confirmPassword" in details:
                #If the passwords are mismatched, return an error.
                if details["password"] != details["confirmPassword"]:
                    return {"error" : "Passwords do not match!"}, 400

                #If the password is too short return an error.
                if len(details["password"]) < 6:
                    return {"error" : "Password is too short!"}, 400

                #Attempts to set the password of the user to match the newly provided password.
                try:
                    user.setPassword(details["password"])
                    db.session.add(user)
                    db.session.commit()

                    #Returns a success message and status code.
                    return {"message" : "Successfully reset password!"}, 200
                except:
                    #Rolls back the database and returns an error and status code.
                    db.session.rollback()
                    return {"error" : "An unknown error has occurred!"}, 500
        else:
            #Otherwise, no password details were provided; return an error and status code.
            return {"error" : "No updated password details provided!"}, 400
    except:
    #Otherwise, the token could not be parsed for that email. Return an error and status code.
        db.session.rollback()
        return {"error" : "Confirmation token is invalid or has expired!"}, 400



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