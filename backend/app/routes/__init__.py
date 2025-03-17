from .users import users_bp
from .patients import patients_bp
from .reports import reports_bp
from .seizures import seizures_bp
from .supplemental_materials import supplemental_materials_bp
from .chats import chats_bp


def register_routes(app):
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(patients_bp, url_prefix="/patients")
    app.register_blueprint(reports_bp, url_prefix="/reports")
    app.register_blueprint(seizures_bp, url_prefix="/seizures")
    app.register_blueprint(
        supplemental_materials_bp, url_prefix="/supplemental_materials"
    )
    app.register_blueprint(chats_bp, url_prefix="/chats")
