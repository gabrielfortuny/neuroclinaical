from app.services.data_upload.nlpRequestHandler import handle_chat_request
from app.services.data_upload.uploadHandlers import docx_upload_handler, pdf_upload_handler
from flask import Blueprint, request, jsonify, send_file
from flask_restful import Api, Resource
from app.models import Patient, Report
from app import db
from flask import current_app
import os

chats_bp = Blueprint("chats", __name__, url_prefix="/chat")
api = Api(chats_bp)

@chats_bp.route("/<int:report_id>/messages", methods=["POST"])
def send_message(report_id):
    supported_file_types = {
    ".pdf": pdf_upload_handler().extract_text_from_pdf,
    ".docx": docx_upload_handler().extract_text_from_docx,
}
    try:
        query_data = request.get_json()
        if not query_data:
            return (
                jsonify({"error": "Invalid Request Format"}),
                401,
            )  # Format is not json readable

        report = db.session.get( Report, report_id)
        if not report:
            current_app.logger.error(f"Error uploading report")
            return 404
        _, content_ext = os.path.splitext(report.file_name)
        current_app.logger.error(f"{content_ext}")
        # Extract text from file
        if content_ext not in supported_file_types:
            return jsonify({"error": "Failed to retrieve reports"}), 500

        extracted_text = supported_file_types[content_ext](report.file_path)
        current_app.logger.error(f"{extracted_text}")
        if not extracted_text:
            return jsonify({"error": "Failed to retrieve reports"}), 500
        
    except Exception as e:
        return jsonify({"error": "Failed to retrieve reports"}), 500# User input
    
    try:
        response = handle_chat_request(extracted_text, query_data["query"])
        return jsonify({"response": response}), 200
    except Exception as e:
           return jsonify({"error": "Error Processing Report"}), 500# User input

    


