import os
import fitz
import traceback
from docx import Document
from flask import current_app
from app.__init__ import db
from app.models import Report
from app.services.data_upload.uploadUtilities import (
    store_drugs_array,
    store_seizures_array,
)

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
    content_ext: str, file_path: str, p_id: int, report: Report
) -> bool:
    """
    Extract text from a document and set a basic summary.
    This simplified version just extracts text and sets a basic summary.
    
    Args:
        content_ext: File extension (pdf, docx)
        file_path: Path to the uploaded file
        p_id: The patient ID this report belongs to
        report: The Report object to update

    Returns:
        True if successful, False otherwise
    """
    current_app.logger.info(f"Starting upload_controller for {content_ext} file: {file_path}")
    
    try:
        # Extract text from file
        if content_ext not in supported_file_types:
            current_app.logger.warning(f"Unsupported file type: {content_ext}")
            return False

        extracted_text = supported_file_types[content_ext](file_path)
        if not extracted_text:
            current_app.logger.warning("No text extracted from file")
            return False

        current_app.logger.info(
            f"Text extracted successfully, length: {len(extracted_text)}"
        )

        # Save a basic summary
        basic_summary = f"Document uploaded for patient {p_id}. File type: {content_ext.upper()}. Size: {len(extracted_text)} characters."
        report.summary = basic_summary
        
        try:
            db.session.commit()
            current_app.logger.info("Updated report with basic summary")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating summary: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            return False

        current_app.logger.info("Upload controller completed successfully")
        return True

    except Exception as e:
        current_app.logger.error(f"Error in upload_controller: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return False
