from flask import Blueprint, request
from flask_restful import Api, Resource
from flask_jwt_extended import create_access_token
from app.models import User
from werkzeug.security import check_password_hash

auth_bp = Blueprint("auth", __name__)
api = Api(auth_bp)


class AuthResource(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            return {"message": "Invalid credentials"}, 401

        access_token = create_access_token(identity=user.id)
        return {"access_token": access_token}, 200


api.add_resource(AuthResource, "/login")
