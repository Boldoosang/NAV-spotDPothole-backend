#Justin Baldeosingh
#SpotDPothole-Backend
#NULLIFY

#ADMIN VIEW - Defines the view endpoints for the admins.

#Imports flask modules.
from flask_jwt_extended import current_user, jwt_required
from flask import Blueprint, redirect, request, jsonify, send_from_directory

from App.controllers.moderator import moderatorBanUser, moderatorDeleteReport, moderatorUnbanUser

#Creates a blueprint to the collection of views for reports.
modViews = Blueprint('modViews', __name__)


@modViews.route('/moderator/removeReport/<reportID>', methods=["DELETE"])
@jwt_required()
def moderatorDeleteReportView(reportID):
    outcome, statusCode = moderatorDeleteReport(current_user, reportID)
    return outcome, statusCode

@modViews.route('/moderator/ban', methods=["POST"])
@jwt_required()
def moderatorBanUserView():
    userDetails = request.get_json()
    outcome, statusCode = moderatorBanUser(current_user, userDetails)
    return outcome, statusCode

@modViews.route('/moderator/unban', methods=["POST"])
@jwt_required()
def moderatorUnbanUserView():
    userDetails = request.get_json()
    outcome, statusCode = moderatorUnbanUser(current_user, userDetails)
    return outcome, statusCode