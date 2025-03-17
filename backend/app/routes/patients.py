from flask import Blueprint
from flask_restful import Api, Resource

patients_bp = Blueprint("users", __name__)
api = Api(patients_bp)
