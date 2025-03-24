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

    current_app.logger.info(
        f"Starting upload_controller for {content_ext} file: {file_path}"
    )

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

        # At the minimum, update the report summary with a basic message about the upload
        try:
            # Use a direct database connection to update the report
            from sqlalchemy import text, create_engine

            # Get database URL
            db_url = current_app.config["SQLALCHEMY_DATABASE_URI"]

            # Update the summary directly
            basic_summary = f"Document uploaded for patient {p_id}. File type: {content_ext.upper()}. Extracted {len(extracted_text)} characters of text."

            engine = create_engine(db_url)
            with engine.connect() as connection:
                connection.execute(
                    text("UPDATE reports SET summary = :summary WHERE id = :id"),
                    {"summary": basic_summary, "id": report.id},
                )
                connection.commit()

            current_app.logger.info("Updated report with basic summary")
        except Exception as e:
            current_app.logger.error(f"Error updating report summary: {str(e)}")

        # Extract days from text
        try:
            days_dict = extract_days_from_text(extracted_text)
            current_app.logger.info(f"Extracted {len(days_dict)} days from text")

            # Process seizures
            try:
                current_app.logger.info("Processing seizures")
                seizures = handle_seizure_request(days_dict)
                current_app.logger.info(f"Found {len(seizures)} seizures")

                # Save the number of seizures found in report.summary
                store_seizures_array(seizures, p_id)
                # engine = create_engine(db_url)
                # with engine.connect() as connection:
                #     connection.execute(
                #         text(
                #             "UPDATE reports SET summary = summary || '\nFound ' || :count || ' seizures.' WHERE id = :id"
                #         ),
                #         {"count": len(seizures), "id": report.id},
                #     )
                #     connection.commit()
            except Exception as e:
                current_app.logger.error(f"Error processing seizures: {str(e)}")

            # Process drugs
            try:
                current_app.logger.info("Processing drugs")
                drugs = handle_drugadmin_request(days_dict)
                current_app.logger.info(f"Found {len(drugs)} drug administrations")

                # Save the number of drugs found in report.summary
                store_drugs_array(drugs, p_id)
                # engine = create_engine(db_url)
                # with engine.connect() as connection:
                #     connection.execute(
                #         text(
                #             "UPDATE reports SET summary = summary || '\nFound ' || :count || ' drug administrations.' WHERE id = :id"
                #         ),
                #         {"count": len(drugs), "id": report.id},
                #     )
                # connection.commit()
            except Exception as e:
                current_app.logger.error(f"Error processing drugs: {str(e)}")

            # Generate summary
            try:
                current_app.logger.info("Generating summary")
                summary = handle_summary_request(extracted_text)

                if (
                    summary and len(summary) > 100
                ):  # Make sure we have a meaningful summary
                    # Save the AI-generated summary to the report
                    report.summary = summary
                    # engine = create_engine(db_url)
                    # with engine.connect() as connection:
                    #     connection.execute(
                    #         text(
                    #             "UPDATE reports SET summary = summary || '\n\nAI Summary:\n' || :ai_summary WHERE id = :id"
                    #         ),
                    #         {"ai_summary": summary, "id": report.id},
                    #     )
                    #     connection.commit()

                    current_app.logger.info(
                        f"Added AI-generated summary of length: {len(summary)}"
                    )
            except Exception as e:
                current_app.logger.error(f"Error generating summary: {str(e)}")

        except Exception as e:
            current_app.logger.error(f"Error extracting days: {str(e)}")
            current_app.logger.error(traceback.format_exc())

        current_app.logger.info("Upload controller completed successfully")
        return True

    except Exception as e:
        current_app.logger.error(f"Error in upload_controller: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return False
