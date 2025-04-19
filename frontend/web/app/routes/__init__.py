from . import dashboard, auth, patient


def register_blueprints(app):
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(patient.bp)
