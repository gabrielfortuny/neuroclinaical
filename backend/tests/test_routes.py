from sqlalchemy import text
from api import User, db


def test_index_route(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert b"Hello from flask" in response.data


def test_test_db_route(test_client):
    response = test_client.get("/test_db")
    assert response.status_code == 200
    assert b"DB Version:" in response.data


def test_test_db_tables_route(test_client):
    response = test_client.get("/test_db_tables")
    assert response.status_code == 200
    assert b"DB Tables:" in response.data


def test_rollback(test_client):
    from api.models import User

    user = User(
        username="rollback_user",
        name="Rollback User",
        email="rollback@example.com",
        password_hash="password",
    )
    db.session.add(user)
    db.session.commit()

    # Attempt to create a duplicate user -> should rollback
    duplicate_user = User(
        username="rollback_user",
        name="Should Fail",
        email="fail@example.com",
        password_hash="password",
    )
    db.session.add(duplicate_user)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()

    # Original user should still be there
    user_from_db = User.query.filter_by(username="rollback_user").first()
    assert user_from_db is not None
    assert user_from_db.email == "rollback@example.com"
