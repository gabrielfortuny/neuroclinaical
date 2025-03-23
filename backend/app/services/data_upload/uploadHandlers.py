import os
import fitz
import typing
import zipfile
import base64
from docx import Document
from io import BytesIO
from flask import current_app
import sqlalchemy
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
from app.__init__ import db
from app.models import Report

# INDIVIDUAL UPLOAD HANDLERS: DON'T USE DIRECTLY


class pdf_upload_handler:
    def extract_text_from_pdf(self, file_path: str) -> str:
        text = []
        with fitz.open(file_path) as pdf:
            for page in pdf:
                text.append(page.get_text())
        return "\n".join(text)

    def __call__(self, file_path: str, p_id: int, report: Report) -> bool:
        # TODO: Write Docstring
        """
        Description:

        Requires:
        Query is a string for the

        Modifies:

        Effects:

        @param data: String to be used for pdf
        """
        text = self.extract_text_from_pdf(
            report.filepath
        )  # Extract raw text from the docx
        return text


class docx_upload_handler:
    def extract_text_from_docx(self, file_path: str) -> str:
        # TODO: Write Docstring
        """
        Description:

        Requires:
        Query is a string for the

        Modifies:

        Effects:

        @param data: String to be used for pdf
        """
        doc = Document(file_path)
        extracted_text = []

        # Extract paragraphs (handling section headers)
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                extracted_text.append(text)

        # Extract tables if present
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells)
                if row_text:
                    extracted_text.append(row_text)

        return "\n".join(extracted_text)

    def __call__(self, file_path: str) -> str:
        """
        Description:

        Requires:

        Modifies:

        Effects:

        @param data: String to be used for docx file
        @param p_id: The Patient ID this report belongs to
        @return: bool indicating successful execution
        """
        text = self.extract_text_from_docx(file_path)  # Extract raw text from the docx
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
    Description: Preforms all steps needed to upload and analyze a document

    Requires:
    Query is a string for the

    Modifies:

    Effects:

    @param content_type: String containing the content type from the request header
    @param content: String containing the file data in base 64 encoding
    @param patient_id: The patient who this report will belong to
    """
    text = ""
    if content_ext in supported_file_types:
        text = supported_file_types[content_ext](file_path)
    else:
        return False
    with open(
        f"{file_path}/report.txt",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(text)
    # Store raw text is same folder as report.txt for easy universal access
    days_dict = extract_days_from_text(
        text
    )  # Extract all days from text into a dictionary

    # TODO: EXTRACT IMAGES

    # HANDLE SEIZURE
    seizures = handle_seizure_request(days_dict)
    if not store_seizures_array(seizures, p_id):
        raise sqlalchemy.exc.SQLAlchemyError

    # HANDLE DRUGS
    drugs = handle_drugadmin_request(days_dict)
    if not store_drugs_array(drugs, p_id):
        raise sqlalchemy.exc.SQLAlchemyError

    # HANDLE SUMMARY
    report.summary = handle_summary_request(text)
    db.session.commit()  # Save changes to out DB "report" object
    return True
