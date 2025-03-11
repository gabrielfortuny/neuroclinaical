from api import User, db


def test_create_user(test_client):
    with test_client.application.app_context():
        user = User(
            username="testuser",
            name="Test User",
            email="test@example.com",
            password_hash="testhash",
        )
        db.session.add(user)
        db.session.commit()

        retrieved_user = User.query.filter_by(username="testuser").first()
        assert retrieved_user is not None
        assert retrieved_user.email == "test@example.com"


def test_unique_username_constraint(test_client):
    user1 = User(
        username="uniqueuser",
        name="User 1",
        email="user1@example.com",
        password_hash="password1",
    )
    db.session.add(user1)
    db.session.commit()

    user2 = User(
        username="uniqueuser",  # Duplicate username should fail
        name="User 2",
        email="user2@example.com",
        password_hash="password2",
    )
    db.session.add(user2)
    with raises(Exception):  # Expect IntegrityError due to unique constraint
        db.session.commit()


from api.models import Patient, Report


def test_cascade_delete(test_client):
    patient = Patient(name="John Doe", dob="2000-01-01")
    db.session.add(patient)
    db.session.commit()

    report = Report(patient_id=patient.id, filepath="/path/to/file.pdf")
    db.session.add(report)
    db.session.commit()

    assert Report.query.count() == 1

    db.session.delete(patient)
    db.session.commit()

    assert Report.query.count() == 0  # Report should be deleted due to cascade
