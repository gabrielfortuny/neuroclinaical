from . import app, db
from sqlalchemy import text


@app.route("/")
def index():
    return "Hello from flask"


@app.route("/test_db")
def test_db():
    try:
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            db_version = result.fetchone()[0]
        return f"DB Version: {db_version}"
    except Exception as e:
        return f"Error: {e}", 500


@app.route("/test_db_tables")
def test_db_tables():
    db_tables = db.inspect(db.engine).get_table_names()
    return f"DB Tables: {db_tables}"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

# import typing
# import threading
# from threading import lock
# from flask import Flask, Blueprint, request, jsonify
# from file_upload.uploadHandlers import pdf_upload_handler, supported_file_types, upload_handler


# app = Flask(__name__)

# Has_run = False

# @app.before_request
# def setup():
#     with lock:
#         if Has_run:
#             pass
#         else:
#             Has_run = True
#             pass
#             #Initialize DB and all that


# @app.route('/upload', methods=['POST'])
# def upload() -> str:
#     #Call Authentication here
#     success = upload_handler(request.content_type, request.content_encoding)
#     #TODO


# @app.route('/testing', methods=["GET"])
# def test() -> str:
#     if request.content_type in supported_file_types:
#         return "OK"
#     return 'Hello World!'


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)
