import os
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required

# Import the direct database utilities
from app.db_utils import (
    get_report,
    update_report_summary,
    store_seizure,
    store_drug
)

# Create a blueprint for report processing
process_bp = Blueprint("process", __name__, url_prefix="/reports")

@process_bp.route("/<int:report_id>/process", methods=["POST"])
def process_report(report_id):
    """
    Process a previously uploaded report to extract seizures, drugs, and generate a summary.
    This endpoint uses direct database connections to avoid Flask-SQLAlchemy app context issues.
    """
    # Import processing functions here to avoid circular imports
    from app.services.data_upload.nlpRequestHandler import (
        handle_seizure_request,
        handle_summary_request,
        handle_drugadmin_request,
    )
    from app.services.data_upload.uploadUtilities import extract_days_from_text
    from app.services.data_upload.uploadHandlers import pdf_upload_handler, docx_upload_handler
    
    # Get the report using direct database access
    report = get_report(report_id)
    if not report:
        return jsonify({"error": "Report not found"}), 404
    
    # Check if file exists
    if not os.path.exists(report['filepath']):
        return jsonify({"error": "Report file not found"}), 404
    
    try:
        # Extract text based on file type
        if report['filetype'] == "pdf":
            extracted_text = pdf_upload_handler()(report['filepath'])
        elif report['filetype'] == "docx":
            extracted_text = docx_upload_handler()(report['filepath'])
        else:
            return jsonify({"error": f"Unsupported file type: {report['filetype']}"}), 400
            
        current_app.logger.info(f"Extracted {len(extracted_text)} characters from {report['filetype']} file")
        
        # Start with a basic summary
        summary = report['summary'] or ""
        summary += f"\nProcessing report on {report['filetype']} file with {len(extracted_text)} characters."
        update_report_summary(report_id, summary)
        
        # Extract days from text
        days_dict = extract_days_from_text(extracted_text)
        current_app.logger.info(f"Extracted {len(days_dict)} days from text")
        
        # Process seizures
        try:
            seizures = handle_seizure_request(days_dict)
            seizure_count = len(seizures)
            current_app.logger.info(f"Found {seizure_count} seizures")
            
            # Update summary with seizure count
            summary += f"\nFound {seizure_count} seizures."
            update_report_summary(report_id, summary)
            
            # Store seizures using direct database access
            successful_seizures = 0
            for seizure in seizures:
                # Get required fields with default values
                day = seizure.get("day", 1)
                
                # Handle different field names for start_time
                start_time = None
                if "start_time" in seizure:
                    start_time = seizure["start_time"]
                elif "seizure_time" in seizure:
                    start_time = seizure["seizure_time"]
                    
                duration = seizure.get("duration", 0)
                
                # Get electrodes
                electrodes = []
                if "electrodes_involved" in seizure and seizure["electrodes_involved"]:
                    electrodes = seizure["electrodes_involved"]
                
                # Store the seizure
                if store_seizure(report['patient_id'], day, start_time, duration, electrodes):
                    successful_seizures += 1
            
            current_app.logger.info(f"Successfully stored {successful_seizures} out of {seizure_count} seizures")
            
        except Exception as e:
            current_app.logger.error(f"Error processing seizures: {str(e)}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            # Continue with other processing
        
        # Process drugs
        try:
            drugs = handle_drugadmin_request(days_dict)
            drug_count = len(drugs)
            current_app.logger.info(f"Found {drug_count} drug administrations")
            
            # Update summary with drug count
            summary += f"\nFound {drug_count} drug administrations."
            update_report_summary(report_id, summary)
            
            # Store drugs using direct database access
            successful_drugs = 0
            for drug in drugs:
                # Get required fields
                if "name" not in drug:
                    continue
                    
                drug_name = drug.get("name", "")
                day = drug.get("day", 1)
                dosage = drug.get("mg_administered", 0)
                
                # Store the drug
                if store_drug(report['patient_id'], drug_name, day, dosage):
                    successful_drugs += 1
            
            current_app.logger.info(f"Successfully stored {successful_drugs} out of {drug_count} drug administrations")
            
        except Exception as e:
            current_app.logger.error(f"Error processing drugs: {str(e)}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            # Continue with other processing
        
        # Generate AI summary
        try:
            ai_summary = handle_summary_request(extracted_text)
            
            if ai_summary and len(ai_summary) > 100:
                summary += f"\n\nAI Summary:\n{ai_summary}"
                update_report_summary(report_id, summary)
                current_app.logger.info(f"Added AI summary of length {len(ai_summary)}")
        except Exception as e:
            current_app.logger.error(f"Error generating AI summary: {str(e)}")
            import traceback
            current_app.logger.error(traceback.format_exc())
        
        return jsonify({
            "message": "Report processed successfully",
            "report_id": report_id
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error processing report: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({"error": f"Error processing report: {str(e)}"}), 500