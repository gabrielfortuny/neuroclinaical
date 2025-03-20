from flask import Blueprint
from flask_restful import Api, Resource

seizures_bp = Blueprint("users", __name__)
api = Api(seizures_bp)
