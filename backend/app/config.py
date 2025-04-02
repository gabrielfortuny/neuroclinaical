import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"

    # Set as absolute path in the container
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")

    # Make sure logging is enabled
    FLASK_LOG_LEVEL = os.getenv("FLASK_LOG_LEVEL", "INFO")

    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_CSRF_PROTECT = False


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
