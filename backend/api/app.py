import typing
import threading
from threading import lock
from flask import Flask, Blueprint, request, jsonify
from file_upload.uploadHandlers import pdf_upload_handler, supported_file_types, upload_handler



app = Flask(__name__)

Has_run = False

@app.before_request
def setup():
    with lock:
        if Has_run:
            pass
        else:
            Has_run = True
            pass
            #Initialize DB and all that


@app.route('/upload', methods=['POST'])
def upload() -> str:  
    #Call Authentication here
    success = upload_handler(request.content_type, request.content_encoding)
    #TODO

    

@app.route('/testing', methods=["GET"])
def test() -> str: 
    if request.content_type in supported_file_types:
        return "OK"
    return 'Hello World!'


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
