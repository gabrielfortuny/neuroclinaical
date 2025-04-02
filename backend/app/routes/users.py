from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource
from app.__init__ import db, jwt
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
    current_user,
    set_access_cookies,
)

from flask import g
from app import db, jwt
from app.models import User
from app.utils.authentication.passwordHandler import (
    check_password_hash,
    hash_password,
)
from app.utils.authentication.authtokenHandler import (
    create_user_token,
    delete_user_token,
)

users_bp = Blueprint("user", __name__, url_prefix="/user")
api = Api(users_bp)


@users_bp.route("/login", methods=["POST"])
def login_user():
    user_data = request.get_json()
    if not user_data:
        return (
            jsonify({"error": "Invalid Request Format"}),
            401,
        )  # Format is not json readable

    user = User.query.filter_by(
        email=user_data["email"]
    ).first()  # Get User with this Email from db
    if not user:  # If Email is not in db, login fails
        return jsonify({"error": "Invalid email or password"}), 401

    if check_password_hash(
        user.password_hash, user_data["password"]
    ):  # Verify the correct password
        access_token = create_user_token(
            user.username, user.id
        )  # Create a new access token
        response = jsonify({"token": access_token})
        set_access_cookies(response, access_token)
        return response, 200  # Return a new access token

    else:  # If the password is wrong, login fails
        return jsonify({"error": "Invalid email or password"}), 401


@users_bp.route("/register", methods=["POST"])
def register_user():
    user_data = request.get_json()
    print(user_data)
    if not user_data:
        return jsonify({"error": "Invalid Request Format"}), 400

    user = User.query.filter_by(
        email=user_data["email"]
    ).first()  # Check for Users with same Email
    if user:
        return jsonify({"error": "Email is already in use"}), 400
    user = User.query.filter_by(
        username=user_data["username"]
    ).first()  # Check for Users with same Username
    if user:
        return jsonify({"error": "Username is already in use"}), 400

    # TODO: ADD PASSWORD STRENGTH VERIFICATION HERE
    p_hash = hash_password(user_data["password"])
    new_user = User(
        username=user_data["username"],
        name=user_data["name"],
        email=user_data["email"],
        password_hash=p_hash,
    )
    db.session.add(new_user)  # Add new user to DB
    db.session.commit()
    access_token = create_user_token(
        new_user.username, new_user.id
    )  # Create access token
    return (
        jsonify(
            {
                "id": new_user.id,
                "username": new_user.username,
                "name": new_user.name,
                "email": new_user.email,
                "token": access_token,
            }
        ),
        201,
    )


@users_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout_user():
    user = current_user  # Ensure token is for valid user in DB
    if user is None:
        return (
            jsonify({"error": "Unauthorized: Missing or Invalid Token"}),
            401,
        )  # User is not in DB / Invalid token
    response = jsonify(
        {
            "message": "User logged out successfully",
            "token": delete_user_token(),
        }
    )
    set_access_cookies(response, delete_user_token())
    return (
        response,
        200,
    )


@users_bp.route("", methods=["PUT"])
@jwt_required()
def user_update_account():
    user = current_user  # Ensure token is for valid user in DB
    if not user:
        return (
            jsonify({"error": "Unauthorized: Missing or Invalid Token"}),
            401,
        )  # User is not in DB / Invalid token
    user_data = request.get_json()  # Convert user data to dict from json
    if not user_data:  # If content type is not json or structure invalid
        return jsonify({"error": "Invalid Request Format"}), 401
    # Update user credentials
    user.name = user_data["name"]
    user.username = user_data["username"]
    user.email = user_data["email"]
    user.password_hash = hash_password(
        user_data["password"]
    )  # Hash new password for storage
    access_token = create_user_token(
        user.username, user.id
    )  # Recreate user token with new username
    db.session.commit()
    response = jsonify({"token": access_token})
    set_access_cookies(response, access_token)
    return (response, 200)  # Respond to valid request resetting token


@users_bp.route("/del", methods=["DELETE"])
@jwt_required()
def delete_user_account():
    print("hello")
    user = current_user  # Ensure token is for valid user in DB
    print("past curre")
    if user is None:
        return (
            jsonify({"error": "Unauthorized: Missing or Invalid Token"}),
            401,
        )  # User is not in DB / Invalid token
    print(user)
    db.session.delete(user)
    db.session.commit()
    return ("", 204)


@users_bp.route("/test", methods=["GET"])
def test_route():
    return jsonify({"message": "Test route works!"}), 200


@users_bp.route("/all", methods=["GET"])
@jwt_required()  # Optional: Only allow authorized users to see all user data
def get_all_users():
    users = User.query.all()  # Get all users from the DB
    results = []
    for user in users:
        results.append(
            {
                "id": user.id,
                "username": user.username,
                "name": user.name,
                "email": user.email,
                # Omit password_hash or other sensitive fields
            }
        )
    return jsonify(results), 200
