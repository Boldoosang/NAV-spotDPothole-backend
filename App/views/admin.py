#Justin Baldeosingh
#SpotDPothole-Backend
#NULLIFY

#ADMIN VIEW - Defines the view endpoints for the admins.

#Imports flask modules.
from flask_jwt_extended import current_user, jwt_required
from flask import Blueprint, redirect, request, jsonify, send_from_directory

from App.controllers.report import deleteUserPotholeReport, getIndividualPotholeReport, getPotholeReports, getReportData, getReportDataForUser, updateReportDescription

#Creates a blueprint to the collection of views for reports.
adminViews = Blueprint('adminViews', __name__)