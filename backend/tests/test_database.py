import pytest
from sqlalchemy import text
from api import app, db


@pytest.fixture(scope="module")
def test_client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


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
