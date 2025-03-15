from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, verify_jwt_in_request
from app.config import Config

db = SQLAlchemy()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        from app import routes, models

        db.create_all()

    @app.before_request
    def require_jwt():
        if request.path != "/auth/login":
            verify_jwt_in_request()

    return app
