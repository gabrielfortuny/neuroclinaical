from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from sqlalchemy import text
from app import db

supplemental_materials_bp = Blueprint("suppleMat", __name__)

@supplemental_materials_bp.route("", methods=["POST"])
# @jwt_required()
def upload_supplemental_material():
    # Verify multipart/form-data request
    if not request.files or 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    # Get file and patient_id from request
    file = request.files['file']
    patient_id = request.form.get('patient_id')
    
    # Validate file exists and has content
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Validate patient_id exists and is a valid integer
    if not patient_id:
        return jsonify({"error": "patient_id is required"}), 400
    
    try:
        patient_id = int(patient_id)
    except ValueError:
        return jsonify({"error": "patient_id must be an integer"}), 400
    
    # Check if patient exists
    result = db.session.execute(
        text("SELECT id FROM patients WHERE id = :patient_id"),
        {"patient_id": patient_id}
    )
    
    if not result.fetchone():
        return jsonify({"error": "Patient not found"}), 404
    
    try:
        # Create a secure filename and save file to appropriate location
        filename = secure_filename(file.filename)
        
        # Create supplemental materials directory if it doesn't exist
        supp_materials_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'supplemental_materials', str(patient_id))
        os.makedirs(supp_materials_dir, exist_ok=True)
        
        # Save file with timestamp to prevent overwriting
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_path = os.path.join(supp_materials_dir, f"{timestamp}_{filename}")
        
        file.save(file_path)
        
        # Create database record for the supplemental material
        # Only including fields that exist in your model
        result = db.session.execute(
            text("""
                INSERT INTO supplemental_materials 
                (patient_id, file_path)
                VALUES (:patient_id, :file_path)
                RETURNING id
            """),
            {
                "patient_id": patient_id,
                "file_path": file_path,
            }
        )
        
        material_id = result.fetchone()[0]
        db.session.commit()
        
        return jsonify({
            "message": "Supplemental material uploaded successfully",
            "material_id": material_id,
            "patient_id": patient_id,
            "file_path": file_path
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error uploading supplemental material: {str(e)}")
        return jsonify({"error": "File processing error"}), 500
    
@supplemental_materials_bp.route("/<int:id>/download", methods=["GET"])
def download_supplemental_material(id):
    # Import required modules
    from flask import send_file, current_app
    from sqlalchemy import text
    from app import db
    import os
    import mimetypes
    
    try:
        # Query the database to get the supplemental material
        result = db.session.execute(
            text("SELECT file_path FROM supplemental_materials WHERE id = :id"),
            {"id": id}
        )
        
        material = result.fetchone()
        
        #if not material or not material.filepath:
        #    return jsonify({"error": "Supplemental material not found"}), 404
            
        # Fix path resolution - ensure we're using absolute path
        file_path = material.file_path
        if not file_path.startswith('/'):
            # If we need to construct a full path
            file_path = os.path.join('/workspaces/project/backend', file_path)
        
        # Remove any './' from the path
        file_path = os.path.normpath(file_path)
            
        # Check if file exists
        if not os.path.exists(file_path):
            current_app.logger.error(f"File not found at path: {file_path}")
            return jsonify({"error": "Supplemental material file not found on server"}), 404
        
        # Get the filename from the path for use in Content-Disposition header
        filename = os.path.basename(file_path)
        
        # Determine content type based on file extension
        content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        
        # Send the file with appropriate headers
        return send_file(
            file_path,
            mimetype=content_type,
            as_attachment=True,
            download_name=filename
        ), 200
        
    except Exception as e:
        current_app.logger.error(f"Error downloading supplemental material: {str(e)}")
        return jsonify({"error": "Failed to download supplemental material"}), 500

@supplemental_materials_bp.route("/<int:id>", methods=["DELETE"])
# @jwt_required()
def delete_supplemental_material(id):
    # Import required modules
    from sqlalchemy import text
    from app import db
    from flask import current_app
    import os
    
    try:
        # First fetch the supplemental material details to get the filepath
        result = db.session.execute(
            text("SELECT file_path FROM supplemental_materials WHERE id = :id"),
            {"id": id}
        )
        
        material = result.fetchone()
        
        if not material:
            return jsonify({"error": "Supplemental material not found"}), 404
            
        # Store filepath for later deletion
        filepath = material.file_path
        
        # Delete the supplemental material from the database
        db.session.execute(
            text("DELETE FROM supplemental_materials WHERE id = :id"),
            {"id": id}
        )
        
        db.session.commit()
        
        # Attempt to delete the actual file
        try:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
            elif filepath:
                # If file doesn't exist at the exact path, try with the corrected base path
                corrected_path = os.path.normpath(os.path.join('/workspaces/project/backend', filepath))
                if os.path.exists(corrected_path):
                    os.remove(corrected_path)
        except Exception as file_error:
            # Log the error but don't affect the API response
            current_app.logger.warning(f"Could not delete file: {str(file_error)}")
        
        # Return success with no content
        return "", 204
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting supplemental material: {str(e)}")
        return jsonify({"error": "Failed to delete supplemental material"}), 500