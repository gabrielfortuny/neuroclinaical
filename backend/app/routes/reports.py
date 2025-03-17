from flask import Blueprint
from flask_restful import Api, Resource

reports_bp = Blueprint("users", __name__)
api = Api(reports_bp)
