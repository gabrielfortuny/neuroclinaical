from flask import Blueprint
from flask_restful import Api, Resource

user_bp = Blueprint("users", __name__)
api = Api(user_bp)


class UserResource(Resource):
    def get(self):
        return {"message": "List of users"}

    def post(self):
        return {"message": "User created"}, 201


api.add_resource(UserResource, "/")
