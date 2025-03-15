from .patient_routes import patient_bp
from .user_routes import user_bp
from .auth_routes import auth_bp


def register_routes(app):
    app.register_blueprint(patient_bp, url_prefix="/patients")
    app.register_blueprint(user_bp, url_prefix="/users")
    app.register_blueprint(auth_bp, url_prefix="/auth")
