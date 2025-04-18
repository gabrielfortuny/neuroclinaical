from backend.app.services.data_upload.nlpRequestHandler import handle_chat_request
from flask import Blueprint, request, jsonify, send_file
from flask_restful import Api, Resource
from app.models import Patient, Report
from app.services.data_upload.uploadHandlers import supported_file_types
from app import db
import os

chats_bp = Blueprint("chats", __name__, url_prefix="/chat")
api = Api(chats_bp)

@chats_bp.route("/{report_id}/messages", methods=["POST"])
def send_message(report_id: int):
    try:
        report = db.session.get(report_id, Report)
        if not report:
            return 404
        _, content_ext = os.path.splitext(report.file_name)
        # Extract text from file
        if content_ext not in supported_file_types:
            return jsonify({"error": "Failed to retrieve reports"}), 500

        extracted_text = supported_file_types[content_ext](report.file_path)
        if not extracted_text:
            return jsonify({"error": "Failed to retrieve reports"}), 500
        
    except Exception as e:
        return jsonify({"error": "Failed to retrieve reports"})# User input
    
    response = handle_chat_request(extracted_text)
    return jsonify({"response": "Failed to retrieve reports"}), 200
    


