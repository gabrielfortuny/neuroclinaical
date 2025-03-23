from flask_jwt_extended import create_access_token


def create_user_token(current_username: str, current_id: int) -> str:
    """
    Description: Creates a token for the user

    Requires:
    User has been authenticated through login page

    Modifies:

    Effects:
    Returns a fresh access token for the user.

    @param current_username: Username of current user
    @param current_id: Id of this user in SQL table
    """
    access_token = (
        create_access_token(  # Create user access token with autoset expiration date
            identity=str(current_id), additional_claims={"username": current_username}
        )
    )
    return access_token  # Return new user access token


def delete_user_token() -> str:
    """
    Description: Sets the token to empty

    Requires:

    Modifies:

    Effects:
    Returns a empty access token for the User.

    """
    return ""


def renew_user_token():
    pass
