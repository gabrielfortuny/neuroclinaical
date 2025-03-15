from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from app.routes import register_routes
from .config import Config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    register_routes(app)

    return app
