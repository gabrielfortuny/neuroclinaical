from app.services.data_upload.uploadHandlers import upload_controller
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import current_user, jwt_required, get_jwt_identity
from flask_restful import Api, Resource
from app.__init__ import db
from app.models import Report, Patient
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from app.services.data_upload.uploadHandlers import upload_controller


reports_bp = Blueprint("reports", __name__, url_prefix="/reports")

api = Api(reports_bp)


@reports_bp.route("", methods=["POST"])
# # @jwt_required()
def upload_report():
    from app import db

    print("uploading report")

    # Verify multipart/form-data request
    if not request.files or "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    # Get file and patient_id from request
    file = request.files["file"]
    patient_id = request.form.get("patient_id")

    # Validate file exists and has content
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Validate patient_id exists and is a valid integer
    if not patient_id:
        return jsonify({"error": "patient_id is required"}), 400

    try:
        patient_id = int(patient_id)
    except ValueError:
        return jsonify({"error": "patient_id must be an integer"}), 400

    # Check if patient exists
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    try:
        # Create a secure filename and save file to appropriate location
        filename = secure_filename(file.filename)

        # Create reports directory if it doesn't exist
        reports_dir = os.path.join(
            current_app.config["UPLOAD_FOLDER"], "reports", str(patient_id)
        )
        os.makedirs(reports_dir, exist_ok=True)

        # Save file with timestamp to prevent overwriting
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_path = os.path.join(reports_dir, f"{timestamp}_{filename}")

        file.save(file_path)
        filetype = os.path.splitext(filename)[1].lower().lstrip(".")
        # Create database record for the report
        new_report = Report(
            patient_id=patient_id,
            summary=f"Report uploaded for patient {patient_id}",
            file_path=file_path,
        )

        if not upload_controller(filetype, file_path, patient_id, new_report):
            raise Exception

        db.session.add(new_report)

        print(f"reports_dir: {reports_dir}")
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Report uploaded successfully",
                    "report_id": new_report.id,
                    "patient_id": patient_id,
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error uploading report: {str(e)}")
        return jsonify({"error": "File processing error"}), 500


@reports_bp.route("/<int:report_id>", methods=["GET"])
def get_report_metadata(report_id):
    # Import required modules
    from sqlalchemy import text
    from app import db
    from flask import current_app

    try:
        # Query the database to get the report metadata
        result = db.session.execute(
            text(
                "SELECT id, patient_id, summary, file_path FROM reports WHERE id = :report_id"
            ),
            {"report_id": report_id},
        )

        report = result.fetchone()

        if not report:
            return jsonify({"error": "Report not found"}), 404

        # Create response data with report metadata
        report_data = {
            "report_id": report.id,
            "patient_id": report.patient_id,
            "summary": report.summary,
            "filepath": report.file_path,
        }

        return jsonify(report_data), 200

    except Exception as e:
        current_app.logger.error(f"Error retrieving report metadata: {str(e)}")
        return jsonify({"error": "Failed to retrieve report metadata"}), 500


@reports_bp.route("/<int:report_id>", methods=["DELETE"])
# @jwt_required()
def delete_report(report_id):
    # Import required modules
    from sqlalchemy import text
    from app import db
    from flask import current_app
    import os

    try:
        # First fetch the report details to get the filepath
        result = db.session.execute(
            text("SELECT filepath FROM reports WHERE id = :report_id"),
            {"report_id": report_id},
        )

        report = result.fetchone()

        if not report:
            return jsonify({"error": "Report not found"}), 404

        # Store filepath for later deletion
        filepath = report.filepath

        # Ensure we're using absolute path
        if not os.path.isabs(filepath):
            filepath = os.path.abspath(filepath)

        # Delete the report from the database
        db.session.execute(
            text("DELETE FROM reports WHERE id = :report_id"), {"report_id": report_id}
        )

        db.session.commit()

        # Attempt to delete the actual file
        try:
            current_app.logger.info(f"Attempting to delete file at: {filepath}")

            if os.path.exists(filepath):
                os.remove(filepath)
                current_app.logger.info(f"Successfully deleted file: {filepath}")
            else:
                current_app.logger.warning(f"File not found at path: {filepath}")
        except Exception as file_error:
            # Log the error but don't affect the API response
            current_app.logger.warning(f"Could not delete file: {str(file_error)}")

        # Return success with no content
        return "", 204

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting report: {str(e)}")
        return jsonify({"error": "Failed to delete report"}), 500


@reports_bp.route("/<int:report_id>/download", methods=["GET"])
def download_report(report_id):
    # Import required modules
    from flask import send_file, current_app
    from sqlalchemy import text
    from app import db
    import os
    import mimetypes

    try:
        # Query the database to get the report
        result = db.session.execute(
            text("SELECT filepath, filetype FROM reports WHERE id = :report_id"),
            {"report_id": report_id},
        )

        report = result.fetchone()

        if not report or not report.filepath:
            return jsonify({"error": "Report not found"}), 404

        # Ensure we're using absolute path
        file_path = report.filepath
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(file_path)

        current_app.logger.info(f"Preparing to download file: {file_path}")

        # Check if file exists
        if not os.path.exists(file_path):
            current_app.logger.error(f"File not found at path: {file_path}")
            return jsonify({"error": "Report file not found on server"}), 404

        # Determine content type based on file extension
        content_type = None
        if report.filetype:
            if report.filetype.lower() == "pdf":
                content_type = "application/pdf"
            elif report.filetype.lower() in ["docx", "doc"]:
                content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif report.filetype.lower() == "txt":
                content_type = "text/plain"
            elif report.filetype.lower() in ["odt"]:
                content_type = "application/vnd.oasis.opendocument.text"
            elif report.filetype.lower() in ["mp4"]:
                content_type = "video/mp4"

        # If we couldn't determine the content type from our mapping, try to guess it
        if not content_type:
            content_type = (
                mimetypes.guess_type(file_path)[0] or "application/octet-stream"
            )

        # Get the filename from the path
        filename = os.path.basename(file_path)

        current_app.logger.info(
            f"Sending file: {filename} with content type: {content_type}"
        )

        # Send the file with appropriate headers
        return send_file(
            file_path, mimetype=content_type, as_attachment=True, download_name=filename
        )

    except Exception as e:
        current_app.logger.error(f"Error downloading report: {str(e)}")
        import traceback

        current_app.logger.error(traceback.format_exc())
        return jsonify({"error": f"Failed to download report: {str(e)}"}), 500
