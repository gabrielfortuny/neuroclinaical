from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, verify_jwt_in_request
from app.config import Config

EXEMPT_PATHS = ["/user/login", "/user/register"]

db = SQLAlchemy()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        # pylint: disable-next=import-outside-toplevel, unused-import
        from app import routes, models

        db.create_all()

    @app.before_request
    def require_jwt():
        if request.path not in EXEMPT_PATHS:
            verify_jwt_in_request()

    return app
