import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")  
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///local.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"

    # Use absolute path if needed
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-jwt")  
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_CSRF_PROTECT = False



class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False