from . import dashboard


def register_blueprints(app):
    app.register_blueprint(dashboard.bp)
