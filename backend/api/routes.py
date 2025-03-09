from flask import Blueprint, request, jsonify
from file_upload.uploadHandlers import supported_file_types

routes = Blueprint("routes", __name__)
Has_run = False

@routes.before_request
def setup():
    pass


@routes.route('/upload', methods=['POST'])
def upload() -> str:  # put application's code here
    if request.content_type in supported_file_types:
        return "OK"
    return 'Hello World!'