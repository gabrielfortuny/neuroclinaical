import os
import fitz
import typing
import zipfile
import base64
import traceback
from docx import Document
from io import BytesIO
from flask import current_app
import sqlalchemy
from app.__init__ import db
from app.models import Report

# INDIVIDUAL UPLOAD HANDLERS: DON'T USE DIRECTLY

class pdf_upload_handler:
    def extract_text_from_pdf(self, file_path: str) -> str:
        try:
            text = []
            with fitz.open(file_path) as pdf:
                for page in pdf:
                    text.append(page.get_text())
            return "\n".join(text)
        except Exception as e:
            current_app.logger.error(f"Error extracting text from PDF: {str(e)}")
            raise Exception(f"PDF extraction failed: {str(e)}")

    def __call__(self, file_path: str) -> str:
        """Extract text from a PDF file."""
        current_app.logger.info(f"Extracting text from PDF: {file_path}")
        text = self.extract_text_from_pdf(file_path)
        current_app.logger.info(f"Extracted {len(text)} characters from PDF")
        return text

class docx_upload_handler:
    def extract_text_from_docx(self, file_path: str) -> str:
        try:
            doc = Document(file_path)
            extracted_text = []

            # Extract paragraphs
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:
                    extracted_text.append(text)

            # Extract tables
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells)
                    if row_text:
                        extracted_text.append(row_text)

            return "\n".join(extracted_text)
        except Exception as e:
            current_app.logger.error(f"Error extracting text from DOCX: {str(e)}")
            raise Exception(f"DOCX extraction failed: {str(e)}")

    def __call__(self, file_path: str) -> str:
        """Extract text from a DOCX file."""
        current_app.logger.info(f"Extracting text from DOCX: {file_path}")
        text = self.extract_text_from_docx(file_path)
        current_app.logger.info(f"Extracted {len(text)} characters from DOCX")
        return text

supported_file_types = {
    "pdf": pdf_upload_handler(),
    "docx": docx_upload_handler(),
}

# DIRECTLY USABLE UPLOAD HANDLERS:

def upload_controller(
    content_ext: str, file_path: str, p_id: int, report
) -> bool:
    """
    Perform all steps needed to upload and analyze a document.
    
    Args:
        content_ext: File extension (pdf, docx)
        file_path: Path to the uploaded file
        p_id: The patient ID this report belongs to
        report: The Report object to update
        
    Returns:
        True if successful, False otherwise
    """
    # Import these here to avoid circular imports
    from app.services.data_upload.nlpRequestHandler import (
        handle_seizure_request,
        handle_summary_request,
        handle_drugadmin_request,
    )
    from app.services.data_upload.uploadUtilities import (
        extract_days_from_text,
        store_drugs_array,
        store_seizures_array,
    )
    
    current_app.logger.info(f"Starting upload_controller for {content_ext} file: {file_path}")
    
    try:
        # Extract text from file
        if content_ext not in supported_file_types:
            current_app.logger.warning(f"Unsupported file type: {content_ext}")
            return False
            
        text = supported_file_types[content_ext](file_path)
        if not text:
            current_app.logger.warning("No text extracted from file")
            return False
            
        current_app.logger.info(f"Text extracted successfully, length: {len(text)}")

        # Extract days from text
        try:
            days_dict = extract_days_from_text(text)
            current_app.logger.info(f"Extracted {len(days_dict)} days from text")
        except Exception as e:
            current_app.logger.error(f"Error extracting days: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            # Fallback - treat all text as day 1
            days_dict = {"1": text}
            current_app.logger.info("Using fallback: all text treated as day 1")

        # Process seizures
        try:
            current_app.logger.info("Processing seizures")
            seizures = handle_seizure_request(days_dict)
            current_app.logger.info(f"Found {len(seizures)} seizures")
            
            if seizures:
                # Use a separate try/except block for database operations
                try:
                    store_result = store_seizures_array(seizures, p_id)
                    if not store_result:
                        current_app.logger.warning("Failed to store seizures")
                except Exception as db_err:
                    current_app.logger.error(f"Database error storing seizures: {str(db_err)}")
            else:
                current_app.logger.info("No seizures to store")
        except Exception as e:
            current_app.logger.error(f"Error processing seizures: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            # Continue processing without failing

        # Process drugs
        try:
            current_app.logger.info("Processing drugs")
            drugs = handle_drugadmin_request(days_dict)
            current_app.logger.info(f"Found {len(drugs)} drug administrations")
            
            if drugs:
                # Use a separate try/except block for database operations
                try:
                    store_result = store_drugs_array(drugs, p_id)
                    if not store_result:
                        current_app.logger.warning("Failed to store drugs")
                except Exception as db_err:
                    current_app.logger.error(f"Database error storing drugs: {str(db_err)}")
            else:
                current_app.logger.info("No drugs to store")
        except Exception as e:
            current_app.logger.error(f"Error processing drugs: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            # Continue processing without failing

        # Generate summary
        try:
            current_app.logger.info("Generating summary")
            summary = handle_summary_request(text)
            if summary:
                # Just update the report summary directly
                report.summary = summary
                try:
                    db.session.commit()
                    current_app.logger.info(f"Summary generated and saved, length: {len(summary)}")
                except Exception as db_err:
                    db.session.rollback()
                    current_app.logger.error(f"Database error saving summary: {str(db_err)}")
                    
                    # Try a different approach - update directly with SQL
                    try:
                        from sqlalchemy import text
                        db.session.execute(
                            text("UPDATE reports SET summary = :summary WHERE id = :id"),
                            {"summary": summary, "id": report.id}
                        )
                        db.session.commit()
                        current_app.logger.info("Summary saved using direct SQL")
                    except Exception as sql_err:
                        db.session.rollback()
                        current_app.logger.error(f"SQL error saving summary: {str(sql_err)}")
            else:
                current_app.logger.warning("Empty summary returned")
                report.summary = "No summary generated."
                try:
                    db.session.commit()
                except Exception as db_err:
                    db.session.rollback()
                    current_app.logger.error(f"Database error saving default summary: {str(db_err)}")
        except Exception as e:
            current_app.logger.error(f"Error generating summary: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            
            # Try to save error message as summary
            try:
                report.summary = f"Error generating summary: {str(e)}"
                db.session.commit()
            except Exception:
                db.session.rollback()
                current_app.logger.error("Failed to save error message as summary")

        current_app.logger.info("Upload controller completed successfully")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Error in upload_controller: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return False