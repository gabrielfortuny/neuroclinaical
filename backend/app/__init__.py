import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, verify_jwt_in_request
from app.config import Config

EXEMPT_PATHS = ["/users/user/login", "/users/user/register", "/users/test", "/hello", "/debug/routes"]

db = SQLAlchemy()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)  # Make Folder for Uploads

    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        # pylint: disable-next=import-outside-toplevel, unused-import
        from app import routes, models

        #We gotta import the actuyal register_routes
        from app.routes import register_routes

        #Call the register func
        register_routes(app)
        db.create_all()

    
    @app.before_request
    def require_jwt():
        if request.path not in EXEMPT_PATHS:
            verify_jwt_in_request()

    return app



    

