from flask_jwt_extended import create_access_token


def create_user_token(current_username: str, current_id: int) -> str:
    """
    Description:

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
            identity=current_id, additional_claims=current_username
        )
    )
    return access_token  # Return new user access token


def delete_user_token():
    pass


def renew_user_token():
    pass
