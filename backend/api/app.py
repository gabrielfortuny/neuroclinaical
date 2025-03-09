import typing
from routes import routes
from flask import Flask

def start_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(routes)
    return app


if __name__ == "__main__":
    app = start_app()
    app.run(host="0.0.0.0", port=5000)
