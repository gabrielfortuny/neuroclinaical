from flask import Blueprint
from flask_restful import Api, Resource

chats_bp = Blueprint("chats", __name__)
api = Api(chats_bp)
