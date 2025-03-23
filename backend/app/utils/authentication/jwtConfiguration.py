from flask import g, json
from app.__init__ import jwt, db
from app.models import User


@jwt.user_lookup_loader
def user_lookup(_jwt_header: json, jwt_data: json) -> bool:
    """
    Description: Configured to support JWT.get_current_user(), don't use this function directly!

    Requires:
    A JWT header exists

    Modifies:

    Effects:
    Returns User object or None if it is not a valid user

    @param _jwt_header: Done by jwt
    @param current_id: Done by jwt
    """
    user_id = jwt_data["sub"]  # Extract the identity from the JWT
    user = None
    try:
        user = db.session.get(User, user_id)  # Lookup the user
    except Exception as err:
        user = None
    if user is None:
        return user
    username = jwt_data.get("username")  # Verify their username
    if user.username != username:
        return None
    return user
