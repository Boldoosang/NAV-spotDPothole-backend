import os, tempfile, pytest, logging
from App.controllers.pothole import getAllPotholes
from App.controllers.user import getOneRegisteredUser, banUserController, unbanUserController
from App.main import create_app, init_db
import time

from App.controllers import *
from App.views import *
from App.models import *

# https://stackoverflow.com/questions/4673373/logging-within-pytest-testshttps://stackoverflow.com/questions/4673373/logging-within-pytest-tests

LOGGER = logging.getLogger(__name__)

# fixtures are used to setup state in the app before the test
@pytest.fixture
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    init_db(app)
    yield app.test_client()
    os.unlink(os.getcwd()+'/App/test.db')

# This fixture depends on create_users which is tested in test #5 test_create_user

@pytest.fixture
def users_in_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    init_db(app)
    createTestUsers()
    yield app.test_client()
    os.unlink(os.getcwd()+'/App/test.db')
    

@pytest.fixture
def simulated_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    init_db(app)
    createSimulatedData()
    yield app.test_client()
    os.unlink(os.getcwd()+'/App/test.db')

########## Unit Tests ########## 
# Unit Test 1: api/potholes should return an empty array when there are no potholes, and should return a status code of 200
def testNoPotholes(empty_db):
    response = empty_db.get('/api/potholes')
    assert b'[]' in response.data and response.status_code == 200

# Unit Test 2: api/reports should return an empty array when there are no potholes, and should return a status code of 200
def testNoReports(empty_db):
    response = empty_db.get('/api/reports')
    assert b'[]' in response.data and response.status_code == 200

# Unit Test 3: api/reports/pothole/<potholeID> should return an empty array when there are no reports for that pothole, and should return a status code of 200
def testNoReportsForPothole(empty_db):
    response = empty_db.get('/api/reports/pothole/1')
    assert b"[]" in response.data and response.status_code == 200

# Unit Test 4: /api/reports/pothole/<potholeID>/report/<reportID> should return an error when there is no pothole with the potholeID, and a status code of 404.
def testNoIndividualReportForPothole(empty_db):
    response = empty_db.get('/api/reports/pothole/1/report/1')
    assert b"No report found." in response.data and response.status_code == 404

# Unit Test 5: /identify should return a message when the user is not logged in, and a return status of 401.
def testIdentifyUserNotLoggedIn(empty_db):
    response = empty_db.get('/identify')
    assert b"msg" in response.data and response.status_code == 401

# Unit Test 6: /api/vote/pothole/<potholeID>/report/<reportID> should return an empty array when there are no votes, and a return status of 200.
def testNoVotesForPothole(empty_db):
    response = empty_db.get('/api/vote/pothole/1/report/1')
    assert b"[]" in response.data and response.status_code == 200

# Unit Test 7: /api/vote/pothole/<potholeID> should return an error when there is no pothole for that potholeID, and a return status of 404.
def testNoIndividualPothole(empty_db):
    response = empty_db.get('/api/potholes/1')
    assert b"No pothole data for that ID." in response.data and response.status_code == 404

# Unit Test 8: /api/reports/pothole/<potholeID>/report/<reportID>/images should return an empty array when there are no reported images, and a return status of 200.
def testNoReportImages(empty_db):
    response = empty_db.get('/api/reports/pothole/1/report/1/images')
    assert b"[]" in response.data and response.status_code == 200

# Unit Test 9: /api/reports/pothole/<potholeID>/report/<reportID>/images/<imageID> should return an error when there is no image for that report, and a return status of 404.
def testNoIndividualReportImage(empty_db):
    response = empty_db.get('/api/reports/pothole/1/report/1/images/1')
    assert b"Pothole image not found!" in response.data and response.status_code == 404


# Unit Test 10: /api/potholes/<potholeID> should return the pothole data for an existing pothole, and a return status of 200.
def testGetExistingPothole(simulated_db):
    potholeJson = b'{"potholeID": 1, "longitude": '
    response = simulated_db.get("/api/potholes/1")
    print(response.data)
    assert potholeJson in response.data and response.status_code == 200

# Unit Test 11: /api/potholes/<potholeID> should return an error for a non-existent pothole, and a return status of 404.
def testGetNonExistentPothole(empty_db):
    response = empty_db.get("/api/potholes/3")
    assert b"No pothole data for that ID." in response.data and response.status_code == 404

# Unit Test 12: /api/potholes/<potholeID>/report/<reportID> should return the report data for an existing report, and a return status of 200.
def testGetExistingReport(simulated_db):
    reportJson = b'{"reportID": 1, "userID": 1, "potholeID": 1,'
    response = simulated_db.get("/api/reports/pothole/1/report/1")
    assert reportJson in response.data and response.status_code == 200

# Unit Test 13: /api/potholes/<potholeID> should return an error for a non-existent report, and a return status of 404.
def testGetNonExistentReport(simulated_db):
    response = simulated_db.get("/api/reports/pothole/1/report/15")
    assert b"No report found." in response.data and response.status_code == 404

# Unit Test 14: /api/potholes/<potholeID> should return an array of reports for a pothole, and a return status of 200.
def testGetAllReportsForPothole(simulated_db):
    reportsJson = b'[{"reportID": 1, "userID": 1, "potholeID": 1,'
    response = simulated_db.get("/api/reports/pothole/1")
    assert reportsJson in response.data and response.status_code == 200

# Unit Test 15: /api/potholes/<potholeID>/report/<reportID>/images should return an array of images for a report, and a return status of 200.
def testGetAllReportImagesForPothole(simulated_db):
    imagesJson = b'[{"imageID": 1, "reportID": 1, "imageURL": "https://firebasestorage.googleapis.com/v0/b/spotdpoth.appspot.com/o/'
    response = simulated_db.get("/api/reports/pothole/1/report/1/images")
    assert imagesJson in response.data and response.status_code == 200

# Unit Test 16: /api/potholes/<potholeID>/report/<reportID>/images/<imageID> should return an image for a report, and a return status of 200.
def testGetIndividualReportImage(simulated_db):
    imageJson = b'{"imageID": 1, "reportID": 1, "imageURL": "https://firebasestorage.googleapis.com/v0/b/spotdpoth.appspot.com/o/'
    response = simulated_db.get("/api/reports/pothole/1/report/1/images/1")
    assert imageJson in response.data and response.status_code == 200

# Unit Test 17: /api/potholes/<potholeID>/report/<reportID>/images/<imageID> should return an error for a non-existent image, and a return status of 404.
def testGetNonExistentIndividualReportImage(simulated_db):
    response = simulated_db.get("/api/reports/pothole/1/report/1/images/13")
    assert b"Pothole image not found!" in response.data and response.status_code == 404

# Unit Test 18: /api/dashboard/potholes should return an error when not logged in, and a return status of 401.
def testGetDashoardPotholesNotLoggedIn(simulated_db):
    response = simulated_db.get("/api/dashboard/potholes")
    assert b"Missing Authorization Header" in response.data and response.status_code == 401


# Unit Test 19: /api/dashboard/potholes should return an error when not logged in, and a return status of 401.
def testGetDashoardReportsNotLoggedIn(simulated_db):
    response = simulated_db.get("/api/dashboard/reports")
    assert b"Missing Authorization Header" in response.data and response.status_code == 401

# Unit Test 20: generate_confirmation_token should generate a valid token from an email address, that can be verified by confirm_token.
def testVerifyConfirmationToken(simulated_db):
    email = "tester1@yahoo.com"
    token = generate_confirmation_token(email)
    returned_email = confirm_token(token)
    assert email == returned_email

# Unit Test 21: confirm_token should return False if a token could not be matched to a user's email address.
def testConfirmationTokenInvalid(simulated_db):
    token = "invalidToken"
    returned_email = confirm_token(token)
    assert returned_email == False


########## Integration Tests ##########  
#Integration Test 1: registerUserController should create a user account using valid data.
def testRegister(empty_db):
    registerUserController({'firstName' : 'Danny', 'lastName' : 'Phantom', 'email' : 'DansPhantom@gmail.com', 'password' : 'danny123', 'confirmPassword' : 'danny123', 'agreeToS' : True})
    userRef = getOneRegisteredUser('DansPhantom@gmail.com')

    checks = True
    if userRef.email != 'DansPhantom@gmail.com' or userRef.firstName != 'Danny' or userRef.lastName != 'Phantom' or userRef.email != 'DansPhantom@gmail.com' or not userRef.checkPassword('danny123'):
        checks = False
    assert checks    

#Integration Test 2: registerUserController should return an appropriate error and status code when registering with invalid data.
def testRegisterInvalidData(empty_db):
    r = registerUserController({'firstName' : 'Mo', 'lastName' : '', 'email' : 'gmail.com', 'password' : '23', 'confirmPassword' : 'danny123', 'agreeToS' : True})   
    assert "Email is invalid!" in r[0]["error"]

#Integration Test 3: registerUserController should return an appropriate error when registering with an existing user email.
def testRegisterExistingUser(empty_db):
    registerUserController({'firstName' : 'Danny', 'lastName' : 'Phantom', 'email' : 'DansPhantom1@gmail.com', 'password' : 'danny123', 'confirmPassword' : 'danny123', 'agreeToS' : True})
    r = registerUserController({'firstName' : 'Danny', 'lastName' : 'Phantom', 'email' : 'DansPhantom1@gmail.com', 'password' : 'danny123', 'confirmPassword' : 'danny123', 'agreeToS' : True})
    assert "User already exists!" in r[0]["error"]

# Integration Test 4: reportPotholeDriver should return a success message when reporting a pothole with valid data.
def testAddNewPotholeReportDriver(users_in_db):
    reportDetails = {
        "longitude" : -61.277001,
        "latitude" : 10.726551,
        "constituencyID" : "arima"
    }

    user1 = getOneRegisteredUser("tester1@yahoo.com")
    r = reportPotholeDriver(user1, reportDetails)


    allReportsByUser = getAllPotholeReportsByUser(user1)
    check2 = False

    for oneReportByUser in allReportsByUser:
        if "Pothole submitted via Driver Mode." == oneReportByUser["description"]:
            check2 = True

    rPotholes = getAllPotholes()
    check1 = False
    for pothole in rPotholes:
        if reportDetails["longitude"] == pothole["longitude"] and reportDetails["latitude"] == pothole["latitude"]:
            check1 = True

    assert check1 and check2 and "Successfully added pothole report to database!" in r[0]["message"] and r[1] == 201


# Integration Test 5: reportPotholeStandard should return a success message when reporting a pothole with valid data.
def testAddNewPotholeReportStandard(users_in_db):
    data = open("App/tests/testImage.txt", "r").read()
    reportDetails = {
        "longitude" : -61.277001,
        "latitude" : 10.726551,
        "constituencyID" : "arima",
        "description": "Very large pothole spanning both lanes of the road.",
        "images" : [
            data
        ]
    }

    user1 = getOneRegisteredUser("tester1@yahoo.com")
    r = reportPotholeStandard(user1, reportDetails, Testing=True)


    allReportsByUser = getAllPotholeReportsByUser(user1)
    check2 = False

    for oneReportByUser in allReportsByUser:
        if reportDetails["description"] == oneReportByUser["description"] and "https://firebasestorage.googleapis.com/v0/b/spotdpoth.appspot.com/o/" in oneReportByUser["reportedImages"][0]["imageURL"]:
            check2 = True

    rPotholes = getAllPotholes()
    check1 = False
    for pothole in rPotholes:
        if reportDetails["longitude"] == pothole["longitude"] and reportDetails["latitude"] == pothole["latitude"]:
            check1 = True

    assert check1 and check2 and "Successfully added pothole report to database!" in r[0]["message"] and r[1] == 201
'''
'''
# Integration Test 6: reportPothole(driver/standard) should return a expiry reset message when reporting a pothole that they previously reported.
def testDuplicateReportSameUser(simulated_db):
    reportDetails = {
        "longitude" : -61.277001,
        "latitude" : 10.726551,
        "constituencyID" : "arima",
    }

    user1 = getOneRegisteredUser("tester1@yahoo.com")
    r = reportPotholeDriver(user1, reportDetails)

    assert "Expiry date of pothole has been reset!" in r[0]["message"] and r[1] == 201


# Integration Test 7: reportPotholeDriver should return a success message when reporting the same pothole using 2 different users.
def testMultipleReportsSamePothole(users_in_db):
    reportDetails = {
        "longitude" : -61.454274,
        "latitude" : 10.432359,
        "constituencyID" : "couva",
    }

    user1 = getOneRegisteredUser("tester1@yahoo.com")
    user2 = getOneRegisteredUser("tester2@yahoo.com")

    reportPotholeDriver(user1, reportDetails)
    reportPotholeDriver(user2, reportDetails)

    user1Reports = getAllPotholeReportsByUser(user1)
    user2Reports = getAllPotholeReportsByUser(user2)

    assert user1Reports[0]["potholeID"] == user2Reports[0]["potholeID"]

# Integration Test 8: deletePotholeReportImage should return a success message when deleting a pothole image as the owner.
def testDeleteExistingPotholeImage(simulated_db):
    user1 = getOneRegisteredUser("tester1@yahoo.com")

    potholeID = 1
    reportID = 1
    imageID = 1

    reportedImageBefore = getIndividualReportedImage(potholeID, reportID, imageID)

    res = deletePotholeReportImage(user1, potholeID, reportID, imageID)

    reportedImageAfter = getIndividualReportedImage(potholeID, reportID, imageID)

    assert reportedImageBefore != reportedImageAfter and "Pothole image successfully deleted!" in res[0]["message"]

# Integration Test 9: deletePotholeReportImage should not allow a user to delete a pothole image that is not owned.
def testDeleteExistingPotholeImageNotOwner(simulated_db):
    user2 = getOneRegisteredUser("tester2@yahoo.com")

    potholeID = 1
    reportID = 1
    imageID = 1

    reportedImageBefore = getIndividualReportedImage(potholeID, reportID, imageID)

    deletePotholeReportImage(user2, potholeID, reportID, imageID)

    reportedImageAfter = getIndividualReportedImage(potholeID, reportID, imageID)

    assert reportedImageBefore == reportedImageAfter

# Integration Test 10: deletePotholeReportImage should return an error message when deleting a pothole image that does not exist.
def testDeleteNonExistentPotholeImage(simulated_db):
    user2 = getOneRegisteredUser("tester2@yahoo.com")

    potholeID = 12
    reportID = 12
    imageID = 12

    reportedImageResult = getIndividualReportedImage(potholeID, reportID, imageID)

    assert "Pothole image not found!" in reportedImageResult[0]["error"]

# Integration Test 11: addPotholeReportImage should return an error message when adding a pothole image to a report that they are not the owner of.
def testAddPotholeImageNotOwner(simulated_db):
    user2 = getOneRegisteredUser("tester2@yahoo.com")
    potholeID = 1
    reportID = 1
    data = open("App/tests/testImage.txt", "r").read()
    imageDetails = {
        "images" : [data]
    }

    rv = addPotholeReportImage(user2, potholeID, reportID, imageDetails)

    print(rv[0])

    assert "You are not the creator of this report!" in rv[0]["error"]

# Integration Test 12: addPotholeReportImage should return a success message when adding a pothole image to a report that is valid.
def testAddPotholeImage(simulated_db):
    user1 = getOneRegisteredUser("tester1@yahoo.com")
    potholeID = 1
    reportID = 1
    data = open("App/tests/testImage.txt", "r").read()
    imageDetails = {
        "images" : [data]
    }

    rv = addPotholeReportImage(user1, potholeID, reportID, imageDetails, Testing=True)

    res = getIndividualReportedImage(potholeID, reportID, 4)

    assert "All images successfully added." in rv[0]["message"] and rv[1] == 201 and "https://firebasestorage.googleapis.com/v0/b/spotdpoth.appspot.com/o/" in res[0]

# Integration Test 13: addPotholeReportImage should return an error message when adding an invalid pothole image to a report that is valid.
def testAddPotholeImageInvalidImage(simulated_db):
    user1 = getOneRegisteredUser("tester1@yahoo.com")
    potholeID = 1
    reportID = 1
    data = "invalidImageBase64String"
    imageDetails = {
        "images" : [data]
    }

    rv = addPotholeReportImage(user1, potholeID, reportID, imageDetails)

    assert "error" in rv[0] and rv[1] == 400

# Integration Test 14: updateReportDescription should return a success message when updating a report that the user is owner of.
def testUpdatePotholeDescriptionAsOwner(simulated_db):
    user1 = getOneRegisteredUser("tester1@yahoo.com")
    potholeID = 1
    reportID = 1
    potholeDetails = {
        'description': 'Wide pothole!'
    }

    rv = updateReportDescription(user1, potholeID, reportID, potholeDetails)
    updatedReport = getIndividualPotholeReport(potholeID, reportID)
    print(updatedReport[0])

    assert "Pothole report description updated!" in rv[0]["message"] and 200 == rv[1] and '"description": "Wide pothole!"' in updatedReport[0]

# Integration Test 15: updateReportDescription should return an error message when updating a report that the user is not the owner of.
def testUpdatePotholeDescriptionAsNonOwner(simulated_db):
    user2 = getOneRegisteredUser("tester2@yahoo.com")
    potholeID = 1
    reportID = 1
    potholeDetails = {
        'description': 'Wide pothole!'
    }

    rv = updateReportDescription(user2, potholeID, reportID, potholeDetails)

    assert "Report does not exist!" in rv[0]["error"] and 404 == rv[1]


# Integration Test 16: updateReportDescription should return an error message when updating a report that does not exist.
def testUpdatePotholeDescriptionNonExistent(simulated_db):
    user2 = getOneRegisteredUser("tester2@yahoo.com")
    potholeID = 12
    reportID = 12
    potholeDetails = {
        'description': 'Wide pothole!'
    }

    rv = updateReportDescription(user2, potholeID, reportID, potholeDetails)

    assert "Report does not exist!" in rv[0]["error"] and 404 == rv[1]

# Integration Test 17: deleteUserPotholeReport should return a success message when deleting a report that is owned.
def testDeleteIndividualReportAsOwner(simulated_db):
    user1 = getOneRegisteredUser("tester1@yahoo.com")
    potholeID = 1
    reportID = 1

    rv = deleteUserPotholeReport(user1, potholeID, reportID)
    oldRep = getIndividualPotholeReport(potholeID, reportID)

    assert "Successfully deleted report." in rv[0]["message"] and 200 == rv[1] and "No report found." in oldRep[0]


# Integration Test 18: deleteUserPotholeReport should return an error message when deleting a report that is not owned.
def testDeleteIndividualReportAsNonOwner(simulated_db):
    user2 = getOneRegisteredUser("tester2@yahoo.com")
    potholeID = 1
    reportID = 1

    rv = deleteUserPotholeReport(user2, potholeID, reportID)
    oldRep = getIndividualPotholeReport(potholeID, reportID)

    assert "Report does not exist! Unable to delete." in rv[0]["error"] and 404 == rv[1] and "No report found." not in oldRep[0]

# Integration Test 19: deleteUserPotholeReport should return an error message when deleting a report that does not exist.
def testDeleteIndividualReportNonExistent(simulated_db):
    user1 = getOneRegisteredUser("tester1@yahoo.com")
    potholeID = 12
    reportID = 12

    rv = deleteUserPotholeReport(user1, potholeID, reportID)

    assert "Report does not exist! Unable to delete." in rv[0]["error"] and 404 == rv[1]

# Integration Test 20: deleteUserPotholeReport should also delete the pothole if the report was the last report for that pothole.
def testDeleteLastReportDeletesPothole(simulated_db):
    user1 = getOneRegisteredUser("tester1@yahoo.com")
    potholeID = 1
    reportID = 1

    potholeBeforeDelete = displayIndividualPotholes(potholeID)[0]

    rv = deleteUserPotholeReport(user1, potholeID, reportID)
    oldRep = getIndividualPotholeReport(potholeID, reportID)

    potholeAfterDelete = displayIndividualPotholes(potholeID)[0]

    assert "Successfully deleted report." in rv[0]["message"] and 200 == rv[1] and "No report found." in oldRep[0] and potholeBeforeDelete != potholeAfterDelete


# Integration Test 21: calculateNetVotes should return the number of upvotes-downvotes for a report.
def testCalculateNetVotes(simulated_db):
    potholeID = 1
    reportID = 1

    user1 = getOneRegisteredUser("tester1@yahoo.com")
    user2 = getOneRegisteredUser("tester2@yahoo.com")
    user3 = getOneRegisteredUser("tester3@yahoo.com")
    user4 = getOneRegisteredUser("tester4@yahoo.com")
    user5 = getOneRegisteredUser("tester5@yahoo.com")
    
    voteOnPothole(user1, potholeID, reportID, {"upvote" : False})
    voteOnPothole(user2, potholeID, reportID, {"upvote" : False})
    voteOnPothole(user3, potholeID, reportID, {"upvote" : True})
    voteOnPothole(user4, potholeID, reportID, {"upvote" : False})
    voteOnPothole(user5, potholeID, reportID, {"upvote" : True})

    netVotes = calculateNetVotes(reportID)

    assert netVotes == -1

# Integration Test 22: reports are automatically deleted if they exceed the negative report threshold.
def testDeleteReportAfterNegativeVoteThreshold(simulated_db):
    potholeID = 1
    reportID = 1

    voteData = {
        "upvote" : False
    }

    user1 = getOneRegisteredUser("tester1@yahoo.com")
    user2 = getOneRegisteredUser("tester2@yahoo.com")
    user3 = getOneRegisteredUser("tester3@yahoo.com")
    user4 = getOneRegisteredUser("tester4@yahoo.com")
    user5 = getOneRegisteredUser("tester5@yahoo.com")
    
    repBefore = getIndividualPotholeReport(potholeID, reportID)
    voteOnPothole(user1, potholeID, reportID, voteData)
    voteOnPothole(user2, potholeID, reportID, voteData)
    voteOnPothole(user3, potholeID, reportID, voteData)
    voteOnPothole(user4, potholeID, reportID, voteData)
    voteOnPothole(user5, potholeID, reportID, voteData)
    repAfter = getIndividualPotholeReport(potholeID, reportID)

    assert "No report found." in repAfter[0] and 404 == repAfter[1] and "No report found." not in repBefore

# Integration Test 23: voteOnPothole should change the number of votes for a report.
def testVoteOnPothole(simulated_db):
    user1 = getOneRegisteredUser("tester1@yahoo.com")
    potholeID = 1
    reportID = 1

    votesBefore = calculateNetVotes(reportID)
    voteOnPothole(user1, potholeID, reportID, {"upvote" : True})
    votesAfter = calculateNetVotes(reportID)

    assert votesBefore != votesAfter

# Integration Test 24: voteOnPothole should unvote on a report if it is submitted to the same report twice with the same vote.
def testUnVoteOnPothole(simulated_db):
    user1 = getOneRegisteredUser("tester1@yahoo.com")
    potholeID = 1
    reportID = 1

    votesBefore = calculateNetVotes(reportID)
    voteOnPothole(user1, potholeID, reportID, {"upvote" : True})
    voteOnPothole(user1, potholeID, reportID, {"upvote" : True})
    votesAfter = calculateNetVotes(reportID)

    assert votesBefore == votesAfter

# Integration Test 25: voteOnPothole should change the vote for a pothole report.
def testChangeVoteOnPothole(simulated_db):
    user1 = getOneRegisteredUser("tester1@yahoo.com")
    potholeID = 1
    reportID = 1

    votesBefore = calculateNetVotes(reportID)
    voteOnPothole(user1, potholeID, reportID, {"upvote" : True})
    votesMidway = calculateNetVotes(reportID)
    voteOnPothole(user1, potholeID, reportID, {"upvote" : False})
    votesAfter = calculateNetVotes(reportID)

    assert votesBefore != votesAfter != votesMidway


# Integration Test 26: Login Controller should return the access token of a user if the credentials are correct, and a status code of 200
def testLoginValid(users_in_db):
    email = "tester1@yahoo.com"
    password = "121233"

    rv = loginUserController({"email" : email, "password": password})
    assert 'access_token' in rv[0] and rv[1] == 200

# Integration Test 27: /login should return an error message if the credentials are invalid, and a status code of 401
def testLoginInvalidData(users_in_db):
    email = "invalidemail"
    password = "121233"

    rv = loginUserController({"email" : email, "password": password})
    assert 'Wrong email or password entered!' in rv[0]["error"] and rv[1] == 401


# Integration Test 28: getUserPotholeData should return an array of potholes reported by a given user.
def testGetDashboardPotholesLoggedIn(simulated_db):
    user = getOneRegisteredUser("tester1@yahoo.com")
    userPotholeData, statusCode = getUserPotholeData(user)
    print(userPotholeData)
    
    assert "error" not in userPotholeData and statusCode == 200

# Integration Test 29: getUserPotholeData should return an empty array of potholes, if the user has no potholes reported.
def testGetDashboardPotholesEmpty(users_in_db):
    user = getOneRegisteredUser("tester1@yahoo.com")
    userPotholeData, statusCode = getUserPotholeData(user)
    print(userPotholeData)
    expected = '[]'
    
    assert expected in userPotholeData and statusCode == 200

# Integration Test 30: getReportDataForUser should return an array of reports reported by a given user.
def testGetDashboardReportsLoggedIn(simulated_db):
    user = getOneRegisteredUser("tester1@yahoo.com")
    userReportData, statusCode = getReportDataForUser(user)
    print(userReportData)
    
    assert "error" not in userReportData and statusCode == 200



# Integration Test 31: getReportDataForUser should return an empty array of reports for a user with no reports.
def testGetDashboardReportsEmpty(users_in_db):
    user = getOneRegisteredUser("tester1@yahoo.com")
    userReportData, statusCode = getReportDataForUser(user)
    print(userReportData)
    expected = '[]'
    
    assert expected in userReportData and statusCode == 200

# Integration Test 32: deleteExpiredPotholes should delete potholes with a passed expiry date.
def testAutoExpiryDeletion(empty_db):
    persistentPothole = Pothole(longitude=10.67, latitude=-61.23, expiryDate=datetime.now() + timedelta(days=30))
    newPothole = Pothole(longitude=10.64, latitude=-61.25, expiryDate=datetime.now())
    db.session.add(persistentPothole)
    db.session.add(newPothole)
    db.session.commit()
    beforeExpiryPotholeCount = len(db.session.query(Pothole).filter_by().all())
    deleteExpiredPotholes()
    afterExpiryPotholeCount = len(db.session.query(Pothole).filter_by().all())
    queriedPersistent = db.session.query(Pothole).filter_by().all()

    
    assert beforeExpiryPotholeCount == 2 and afterExpiryPotholeCount == 1 and persistentPothole in queriedPersistent

# Integration Test 33: A banned user should receive a banned message when attempting to login.
def testBannedUserLogin(users_in_db):
    user = getOneRegisteredUser("tester6@yahoo.com")
    banUserController("tester6@yahoo.com")

    email = "tester6@yahoo.com"
    password = "121233"

    rv = loginUserController({"email" : email, "password": password})

    assert 'User is banned.' in rv[0]["error"] and rv[1] == 403


# Integration Test 34: A banned user who is then unbanned should be able to login.
def testUnbannedUserLogin(users_in_db):
    user = getOneRegisteredUser("tester6@yahoo.com")
    banUserController("tester6@yahoo.com")

    email = "tester6@yahoo.com"
    password = "121233"

    rv1 = loginUserController({"email" : email, "password": password})
    unbanUserController("tester6@yahoo.com")
    rv2 = loginUserController({"email" : email, "password": password})

    assert 'User is banned.' in rv1[0]["error"] and rv1[1] == 403 and 'access_token' in rv2[0] and rv2[1] == 200


# Integration Test 35: A banned user should receive a banned message when attempting to vote.
def testBannedUserVote(simulated_db):
    user = getOneRegisteredUser("tester6@yahoo.com")
    banUserController("tester6@yahoo.com")

    rv1 = voteOnPothole(user, 1, 1, {"upvote" : False})

    assert 'User is banned.' in rv1[0]["error"] and rv1[1] == 403


# Integration Test 36: A banned user should receive a banned message when attempting to file a standard report.
def testBannedUserStandardReport(simulated_db):
    user = getOneRegisteredUser("tester6@yahoo.com")
    banUserController("tester6@yahoo.com")

    #do task here
    reportDetails = {
        "longitude" : -61.277001,
        "latitude" : 10.726551,
        "constituencyID" : "arima",
        "description": "Very large pothole spanning both lanes of the road.",
        "images" : [
            "https://www.howtogeek.com/wp-content/uploads/2018/08/Header.png"
        ]
    }

    rv1 = reportPotholeStandard(user, reportDetails, Testing=True)

    assert 'User is banned.' in rv1[0]["error"] and rv1[1] == 403


# Integration Test 37: A banned user should receive a banned message when attempting to file a driver report.
def testBannedUserDriverReport(simulated_db):
    user = getOneRegisteredUser("tester6@yahoo.com")
    banUserController("tester6@yahoo.com")

    #do task here
    reportDetails = {
        "longitude" : -61.277001,
        "latitude" : 10.726551
    }

    rv1 = reportPotholeDriver(user, reportDetails)

    assert 'User is banned.' in rv1[0]["error"] and rv1[1] == 403

# Integration Test 38: A banned user should receive a banned message when attempting to add an image to their report.
def testBannedUserAddImage(simulated_db):
    user = getOneRegisteredUser("tester1@yahoo.com")
    banUserController("tester1@yahoo.com")
    potholeID = 1
    reportID = 1

    #do task here
    imageDetails = {
        "images" : ["https://media.gettyimages.com/photos/balanced-stones-on-a-pebble-beach-during-sunset-picture-id157373207?s=612x612"]
    }

    rv1 = addPotholeReportImage(user, potholeID, reportID, imageDetails)
    assert 'User is banned.' in rv1[0]["error"] and rv1[1] == 403


# Integration Test 39: A banned user should receive a banned message when attempting to delete an image from a report.
def testBannedUserDeleteImage(simulated_db):
    user = getOneRegisteredUser("tester1@yahoo.com")
    banUserController("tester1@yahoo.com")
    potholeID = 1
    reportID = 1
    imageID = 1

    rv1 = deletePotholeReportImage(user, potholeID, reportID, imageID)
    assert 'User is banned.' in rv1[0]["error"] and rv1[1] == 403

# Integration Test 40: A banned user should receive a banned message when attempting to delete the entire report.
def testBannedUserDeleteReport(simulated_db):
    user = getOneRegisteredUser("tester1@yahoo.com")
    banUserController("tester1@yahoo.com")
    potholeID = 1
    reportID = 1

    rv1 = deleteUserPotholeReport(user, potholeID, reportID)

    assert 'User is banned.' in rv1[0]["error"] and rv1[1] == 403

# Integration Test 41: A banned user should receive a banned message when attempting to edit the pothole description.
def testBannedUserDeleteReport(simulated_db):
    user = getOneRegisteredUser("tester1@yahoo.com")
    banUserController("tester1@yahoo.com")
    potholeID = 1
    reportID = 1
    description = "New Description!"
    potholeDetails = {
        "description": description
    }

    rv1 = updateReportDescription(user, potholeID, reportID, potholeDetails)

    assert 'User is banned.' in rv1[0]["error"] and rv1[1] == 403 and description not in getIndividualPotholeReport(potholeID, reportID)


# Integration Test 42: A success message should be returned to the user upon successful password change.
def testChangePasswordValid(users_in_db):
    email = "tester1@yahoo.com"
    password = "121233"
    newPassword = "newTestPassword123"
    user = getOneRegisteredUser(email)
    newPasswordDetails = {
        "oldPassword": password,
        "password": newPassword,
        "confirmPassword": newPassword
    }
    
    #Before changing password
    rv1 = loginUserController({"email" : email, "password": password})
    #Changing Password
    rv2 = changePassword(user, newPasswordDetails)
    #Login with new password
    rv3 = loginUserController({"email" : email, "password": newPassword})

    assert 'Successfully changed password!' in rv2[0]["message"] and rv2[1] == 200 and 'access_token' in rv1[0] and rv1[1] == 200 and 'access_token' in rv3[0] and rv3[1] == 200


# Integration Test 43: An error message should be returned to the user upon attempting a password change when not logged in.
def testChangePasswordNotLoggedIn(users_in_db):
    password = "121233"
    newPassword = "newTestPassword123"
    user = None
    newPasswordDetails = {
        "oldPassword": password,
        "password": newPassword,
        "confirmPassword": newPassword
    }
    
    #Changing Password
    rv2 = changePassword(user, newPasswordDetails)
    print(rv2)
    assert 'You are not logged in!' in rv2[0]["error"] and rv2[1] == 400

# Integration Test 44: An error message should be returned to the user upon attempting to change the password with a wrong original password.
def testChangePasswordWrongOriginal(users_in_db):
    email = "tester1@yahoo.com"
    password = "121233"
    wrongPassword = "defAWrongPassword"
    newPassword = "newTestPassword123"
    user = getOneRegisteredUser(email)
    newPasswordDetails = {
        "oldPassword": wrongPassword,
        "password": newPassword,
        "confirmPassword": newPassword
    }
    
    #Before changing password
    rv1 = loginUserController({"email" : email, "password": password})
    #Changing Password
    rv2 = changePassword(user, newPasswordDetails)
    #Login with new password
    rv3 = loginUserController({"email" : email, "password": newPassword})

    assert 'The original password you have entered is incorrect!' in rv2[0]["error"] and rv2[1] == 400 and 'access_token' in rv1[0] and rv1[1] == 200 and 'error' in rv3[0] and rv3[1] == 401


# Integration Test 45: An error message should be returned to the user upon attempting to change the password with an invalid new password.
def testChangePasswordInvalidNew(users_in_db):
    email = "tester1@yahoo.com"
    password = "121233"
    invalidNewPassword = "12"
    user = getOneRegisteredUser(email)
    newPasswordDetails = {
        "oldPassword": password,
        "password": invalidNewPassword,
        "confirmPassword": invalidNewPassword
    }
    
    #Before changing password
    rv1 = loginUserController({"email" : email, "password": password})
    #Changing Password
    rv2 = changePassword(user, newPasswordDetails)
    #Login with new password
    rv3 = loginUserController({"email" : email, "password": invalidNewPassword})

    assert 'Password is too short!' in rv2[0]["error"] and rv2[1] == 400 and 'access_token' in rv1[0] and rv1[1] == 200 and 'error' in rv3[0] and rv3[1] == 401


# Integration Test 46: sendPasswordResetControllers should return a success message and code if attempting to reset an account that exists with the email.
def testSendPasswordResetValid(users_in_db):
    email = "tester1@yahoo.com"
    details = {
        "email" : email
    }
    rv = sendPasswordResetController(details, testing=True)

    assert 'Password reset email resent!' in rv[0]["message"] and rv[1] == 200

# Integration Test 47: sendPasswordResetControllers should return an error message and code if attempting to reset an account that does not exist with the email.
def testSendPasswordResetUnregisteredEmail(users_in_db):
    email = "notRegisteredAccount@yahoo.com"
    details = {
        "email" : email
    }
    rv = sendPasswordResetController(details, testing=True)

    assert 'Unregistered email provided!' in rv[0]["error"] and rv[1] == 404

# Integration Test 48: sendPasswordResetControllers should return an error message and code if attempting to reset an account with no supplied email.
def testSendPasswordResetUnregisteredEmail(users_in_db):
    email = None
    details = {
        "email" : email
    }
    rv = sendPasswordResetController(details, testing=True)

    assert 'Unregistered email provided!' in rv[0]["error"] and rv[1] == 404

# Integration Test 49: resendConfirmationController should return a success message and code if attempting to resend a confirmation for an existing, unconfirmed email.
def testResendConfirmationValid(users_in_db):
    email = "DansPhantom@gmail.com"
    registerUserController({'firstName' : 'Danny', 'lastName' : 'Phantom', 'email' : email, 'password' : 'danny123', 'confirmPassword' : 'danny123', 'agreeToS' : True}, testConfirmed=False, testing=True)
    
    details = {
        "email" : email
    }
    rv = resendConfirmationController(details, testing=True)
    assert 'Confirmation email resent!' in rv[0]["message"] and rv[1] == 200

# Integration Test 50: resendConfirmationController should return an error message and code if attempting to resend a confirmation for an already confirmed email.
def testResendConfirmationAlreadyConfirmed(users_in_db):
    email = "tester1@yahoo.com"
    
    details = {
        "email" : email
    }

    rv = resendConfirmationController(details, testing=True)
    assert 'Email address not registered or user already confirmed!' in rv[0]["error"] and rv[1] == 400


# Integration Test 51: resendConfirmationController should return an error message and code if attempting to resend a confirmation for an unregistered email.
def testResendConfirmationUnregisteredEmail(users_in_db):
    email = "unRegisteredEmail@yahoo.com"
    
    details = {
        "email" : email
    }

    rv = resendConfirmationController(details, testing=True)
    assert 'Email address not registered or user already confirmed!' in rv[0]["error"] and rv[1] == 400

# Integration Test 52: resendConfirmationController should return an error message and code if attempting to resend a confirmation for an invalid email.
def testResendConfirmationInvalidEmail(users_in_db):
    email = None
    
    details = {
        "email" : email
    }

    rv = resendConfirmationController(details, testing=True)
    assert 'Email address not registered or user already confirmed!' in rv[0]["error"] and rv[1] == 400

# Integration Test 53: confirmEmailController should return a successful confirmation message if confirming a valid user who has not already been confirmed.
def testConfirmEmailValidToken(users_in_db):
    email = "DansPhantom@gmail.com"
    registerUserController({'firstName' : 'Danny', 'lastName' : 'Phantom', 'email' : email, 'password' : 'danny123', 'confirmPassword' : 'danny123', 'agreeToS' : True}, testConfirmed=False, testing=True)
    
    details = {
        "email" : email
    }

    token = generate_confirmation_token(email)

    rv = confirmEmailController(token, details)
    
    assert 'User has been confirmed. You may now login.' in rv[0]["message"] and rv[1] == 200


# Integration Test 54: confirmEmailController should return a success message if confirming a user who has already been confirmed.
def testConfirmEmailAlreadyConfirmed(users_in_db):
    email = "tester1@yahoo.com"

    details = {
        "email" : email
    }

    token = generate_confirmation_token(email)

    rv = confirmEmailController(token, details)
    
    assert 'User already confirmed!' in rv[0]["message"] and rv[1] == 200

# Integration Test 55: confirmEmailController should return an error message if confirming a user who is not registered.
def testConfirmEmailUnregistered(users_in_db):
    email = "unregisteredEmail@yahoo.com"

    details = {
        "email" : email
    }

    token = generate_confirmation_token(email)

    rv = confirmEmailController(token, details)
    
    assert 'Email address not registered!' in rv[0]["error"] and rv[1] == 400


# Integration Test 56: confirmEmailController should return an error message if confirming a user with a token of another user.
def testConfirmEmailTokenOfAnotherAccount(users_in_db):
    email = "DansPhantom@gmail.com"
    registerUserController({'firstName' : 'Danny', 'lastName' : 'Phantom', 'email' : email, 'password' : 'danny123', 'confirmPassword' : 'danny123', 'agreeToS' : True}, testConfirmed=False, testing=True)
    
    alreadyRegisteredEmail = 'tester1@yahoo.com'

    details = {
        "email" : email
    }

    token = generate_confirmation_token(alreadyRegisteredEmail)

    rv = confirmEmailController(token, details)
    
    assert 'Token is not associated with this email address or is invalid!' in rv[0]["error"] and rv[1] == 400


# Integration Test 57: confirmEmailController should return an error message if confirming a user with an invalid token.
def testConfirmEmailInvalidToken(users_in_db):
    email = "DansPhantom@gmail.com"
    registerUserController({'firstName' : 'Danny', 'lastName' : 'Phantom', 'email' : email, 'password' : 'danny123', 'confirmPassword' : 'danny123', 'agreeToS' : True}, testConfirmed=False, testing=True)
    
    details = {
        "email" : email
    }

    token = "invalidToken"

    rv = confirmEmailController(token, details)
    
    assert 'Token is not associated with this email address or is invalid!' in rv[0]["error"] and rv[1] == 400

# Integration Test 58: resetPasswordController should return a success message when resetting a password with valid details.
def testResetPasswordControllerValid(users_in_db):
    email = "tester1@yahoo.com"
    password = "121233"
    newPassword = "333333"

    details = {
        "email" : email,
        "password" : newPassword,
        "confirmPassword" : newPassword
    }

    beforeReset = loginUserController({"email" : email, "password": password})

    token = generate_confirmation_token(email)
    rv = resetPasswordController(details, token)
    
    afterReset = loginUserController({"email" : email, "password": newPassword})

    assert 'Successfully reset password!' in rv[0]["message"] and rv[1] == 200 and 'access_token' in beforeReset[0] and beforeReset[1] == 200 and 'access_token' in afterReset[0] and afterReset[1] == 200

# Integration Test 59: resetPasswordController should return an error when resetting a password for an account that does not exist.
def testResetPasswordControllerUnregistered(users_in_db):
    email = "unregisteredAccount@yahoo.com"
    password = "121233"
    newPassword = "333333"

    details = {
        "email" : email,
        "password" : newPassword,
        "confirmPassword" : newPassword
    }

    token = generate_confirmation_token(email)
    rv = resetPasswordController(details, token)

    assert 'Email address not registered!' in rv[0]["error"] and rv[1] == 404 

# Integration Test 60: resetPasswordController should return an error when resetting a password for an account with an invalid token.
def testResetPasswordControllerInvalidToken(users_in_db):
    email = "tester1@yahoo.com"
    password = "121233"
    newPassword = "333333"

    details = {
        "email" : email,
        "password" : newPassword,
        "confirmPassword" : newPassword
    }

    token = "invalid token"
    rv = resetPasswordController(details, token)

    assert 'Token is not associated with this email address or is invalid!' in rv[0]["error"] and rv[1] == 400 

# Integration Test 61: resetPasswordController should return an error when resetting a password for an account with an another account's token.
def testResetPasswordControllerOtherAccountToken(users_in_db):
    otherAccount = "tester2@yahoo.com"
    email = "tester1@yahoo.com"
    password = "121233"
    newPassword = "333333"

    details = {
        "email" : email,
        "password" : newPassword,
        "confirmPassword" : newPassword
    }

    token = generate_confirmation_token(otherAccount)
    rv = resetPasswordController(details, token)

    assert 'Token is not associated with this email address or is invalid!' in rv[0]["error"] and rv[1] == 400 


# Integration Test 62: resetPasswordController should return an error when resetting a password using weak password criteria.
def testResetPasswordControllerWeakPassword(users_in_db):
    email = "tester1@yahoo.com"
    password = "121233"
    newPassword = "weak"

    details = {
        "email" : email,
        "password" : newPassword,
        "confirmPassword" : newPassword
    }

    token = generate_confirmation_token(email)
    rv = resetPasswordController(details, token)

    assert 'Password is too short!' in rv[0]["error"] and rv[1] == 400 



# Integration Test 63: resetPasswordController should return an error when resetting a password with mismatched updated passwords.
def testResetPasswordControllerMismatchedPassword(users_in_db):
    email = "tester1@yahoo.com"
    password = "121233"
    newPassword = "weakened"
    newPasswordConfirm = "mismatched"

    details = {
        "email" : email,
        "password" : newPassword,
        "confirmPassword" : newPasswordConfirm
    }

    token = generate_confirmation_token(email)
    rv = resetPasswordController(details, token)

    assert 'Passwords do not match!' in rv[0]["error"] and rv[1] == 400 