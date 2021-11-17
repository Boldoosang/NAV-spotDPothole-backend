#Justin Baldeosingh
#SpotDPothole-Backend
#NULLIFY

#USERREPORTVOTE CONTROLLERS - Facilitate interactions between the userReportVote model and the other models/controllers of the application.

#CONSTANTS
#Defines the minimum net vote threshold that would result in the deletion of a report.
REPORT_DELETION_THRESHOLD = -5          

#Imports flask modules, json, and geopy.
from flask import Flask, request, session
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, current_user
from geopy import distance
import json

#Imports the all of the models and controllers of the application.
from App.models import *
from App.controllers import *

#Returns all of the votes for a particular reportID.
def getAllVotesForReport(reportID):
    #Gets all of the votes for a particular report, stores their dictionary definition in an array, and returns a json dump of the array.
    #Also returns an 'OK' http status code (200).
    votes = db.session.query(UserReportVote).filter_by(reportID=reportID).all()
    voteData = [v.toDict() for v in votes]
    return json.dumps(voteData), 200

#Returns all of the upvotes for a particular reportID.
def getAllUpvotesForReport(reportID):
    #Gets all of the upvotes for a particular report, stores their dictionary definition in an array, and returns a json dump of the array.
    #Also returns an 'OK' http status code (200).
    upvotes = db.session.query(UserReportVote).filter_by(reportID=reportID, upvote=True).all()
    upvoteData = [uv.toDict() for uv in upvotes]
    return json.dumps(upvoteData), 200

#Returns all of the downvotes for a particular reportID.
def getAllDownvotesForReport(reportID):
    #Gets all of the downvotes for a particular report, stores their dictionary definition in an array, and returns a json dump of the array.
    #Also returns an 'OK' http status code (200).
    downvotes = db.session.query(UserReportVote).filter_by(reportID=reportID, upvote=False).all()
    downvoteData = [dv.toDict() for dv in downvotes]
    return json.dumps(downvoteData), 200

#Enables a user to vote on a pothole report and returns the outcome along with the http status code.
def voteOnPothole(user, potholeID, reportID, voteData):
    #If voteData is null, return an error that no data was provided along with the 'BAD REQUEST' http status code (400).
    if not voteData:
        return {"error": "No vote data supplied."}, 400

    #If there is no 'upvote' key in voteData, return an error that an invalid request was submitted and a 'BAD REQUEST' http status code (400).
    if "upvote" not in voteData:
        return {"error": "Invalid vote request submitted"}, 400

    #Finds the report associated with the potholeID and reportID, from the database.
    report = db.session.query(Report).filter_by(potholeID=potholeID, reportID=reportID).first()

    #If the report exists, facilitate the voting process.
    if(report):
        #Determines if the user has already voted on this report and stores the vote object associated with the vote.
        existingVote = db.session.query(UserReportVote).filter_by(userID=user.userID, reportID=reportID).first()
        
        #Determines if the upvote key of the dictionary consists of binary values before processing them.
        if voteData["upvote"] == False or voteData["upvote"] == True:
            #Attempts to vote on a report.
            try:
                #Attempts to vote on a report given that the user has not previously voted on the report.
                if not existingVote: 
                    #Creates a new vote object with the vote data, adds the vote, and commits it to the database.
                    newVote = UserReportVote(reportID = reportID, upvote = voteData["upvote"], userID = user.userID)
                    db.session.add(newVote)
                    db.session.commit()

                    #If the net votes changes such that the net votes are now below the deletion threshold, delete the pothole report.
                    if calculateNetVotes(reportID) <= REPORT_DELETION_THRESHOLD:
                        #Deletes the pothole report for a given reportID and potholeID.
                        deletePotholeReport(potholeID, reportID)
                        #Returns a message that the report will be deleted, along with an 'OK' http status code.
                        return {"message": "This report will be deleted due to its severe negative reputation."}, 200

                    #Returns a message that the vote was casted for the report along with a 'CREATED' http status code (201).
                    return {"message": "Vote casted for report!"}, 201
                else:
                #Attempts to vote on a report given that the user has previously voted on the report.
                    #If the vote option received matches the previous vote option, the user has toggled the vote and would result in the deletion of the vote.
                    if existingVote.upvote == voteData["upvote"]:
                        #Deletes the vote, commits the changes, and returns a message along with a 'OK' http status code.
                        db.session.delete(existingVote)
                        db.session.commit()
                        return {"message": "Vote removed from report!"}, 200
                    #Otherwise, if the vote option is different than the previous vote, update the vote information.
                    else:
                        #Changes the vote status, adds the vote to the database, and commits the changes.
                        existingVote.upvote = voteData["upvote"]
                        db.session.add(existingVote)
                        db.session.commit()

                        #If the net votes changes such that the net votes are now below the deletion threshold, delete the pothole report.
                        if calculateNetVotes(reportID) <= REPORT_DELETION_THRESHOLD:
                            #Deletes the pothole report for a given reportID and potholeID.
                            deletePotholeReport(potholeID, reportID)
                            #Returns a message that the report will be deleted, along with an 'OK' http status code.
                            return {"message": "This report will be deleted due to its severe negative reputation."}, 200

                        return {"message": "Vote updated for report!"}, 200
            #If voting on a report fails, rollback the database and return an error and an appropriate 'INTERNAL SERVER ERROR' http status code.
            except :
                db.session.rollback()
                return {"error": "Error voting for this report!"}, 500
        #Otherwise, if the vote data for the upvote field does not consist of True or False, it is invalid.
        #Return an error and a 'BAD REQUEST' http status code.
        else:
            return {"error": "Invalid vote data supplied!"}, 400

    #Otherwise, if the report does not exists, return an appropriate error and 'NOT FOUND' http status code.
    else:
        return {"error": "No report found."}, 404

#Calculates and returns the net vote outcome for a particular report.
def calculateNetVotes(reportID):
    #Finds the number of upvotes and downvotes for a particular report, in the vote database.
    upvotes = db.session.query(UserReportVote).filter_by(reportID=reportID, upvote=True).count()
    downvotes = db.session.query(UserReportVote).filter_by(reportID=reportID, upvote=False).count()
    #Returns the net upvotes-downvotes.
    return (upvotes-downvotes)