from flask import Blueprint
from flask_restful import Api, Resource

users_bp = Blueprint("users", __name__)
api = Api(users_bp)
