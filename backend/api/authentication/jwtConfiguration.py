from flask import g, json
from backend.app.__init__ import jwt, db


@jwt.user_lookup_loader
def user_lookup(_jwt_header: json, jwt_data: json) -> bool:
    """
    Description: Configured to support JWT.get_current_user(), don't use this function directly!

    Requires:
    A JWT header exists
    Modifies:
    Global flask variable g.current_user is updated for this request
    Effects:

    @param _jwt_header: Done by jwt
    @param current_id: Done by jwt
    """
    user_id = jwt_data["sub"]  # Extract the identity from the JWT
    user = db.session.get(user_id)  # Lookup the user
    g.current_user = user  # Attach user to the Flask global object
    return user
