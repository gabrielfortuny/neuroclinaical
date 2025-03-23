from flask import Blueprint
from flask_restful import Api, Resource

supplemental_materials_bp = Blueprint("users", __name__)
api = Api(supplemental_materials_bp)
