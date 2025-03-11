import pytest
from api import app, db


@pytest.fixture
def test_client():
    # Set up the Flask test client
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()  # Create tables in memory for the test database
        client = app.test_client()
        yield client
        db.session.remove()
        db.drop_all()
