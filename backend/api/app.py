import typing
from routes import routes
from flask import Flask

app = Flask(__name__)

def start_app(a: Flask) -> Flask:
    app.register_blueprint(routes)
    return app


if __name__ == "__main__":
    app = start_app(app)
    app.run(host="0.0.0.0", port=5000)
