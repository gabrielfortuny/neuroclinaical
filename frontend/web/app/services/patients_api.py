"""API requests for patients."""

import os
import requests
from flask import current_app


def fetch_all_patients():
    """Fetch a list of all patients."""
    url = f"{current_app.config['API_BASE_URL']}/patients"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        current_app.logger.error(f"API error: {e}")
        return []


def create_new_patient(name: str):
    """Create a new patient"""
    url = f"{current_app.config['API_BASE_URL']}/patients"
    data = {"name": name}
    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        current_app.logger.error(f"API error: {e}")
        return []


def fetch_a_patient(patient_id: int):
    """Fetch a specific patient by ID"""
    url = f"{current_app.config['API_BASE_URL']}/patients/{patient_id}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        current_app.logger.error(f"API error: {e}")
        return None


def update_a_patient(patient_id: int, name: str):
    """Update an existing patient by ID"""
    url = f"{current_app.config['API_BASE_URL']}/patients/{patient_id}"
    data = {"name": name}
    try:
        response = requests.patch(url, json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        current_app.logger.error(f"API error: {e}")
        return None


def delete_a_patient(patient_id: int):
    """Delete a patient by ID"""
    url = f"{current_app.config['API_BASE_URL']}/patients/{patient_id}"
    try:
        response = requests.delete(url, timeout=10)
        response.raise_for_status()
        return True  # Successfully deleted
    except requests.RequestException as e:
        current_app.logger.error(f"API error: {e}")
        return False


def upload_report(patient_id: int, file_path: str):
    """Upload a report for a specific patient."""
    url = f"{current_app.config['API_BASE_URL']}/reports"
    file_name = os.path.basename(file_path)
    try:
        with open(file_path, "rb") as file:
            files = {"file": (file_name, file)}
            data = {"patient_id": patient_id}
            response = requests.post(url, files=files, data=data, timeout=10)
            response.raise_for_status()
            return response.json()  # Return the response from the backend
    except requests.RequestException as e:
        current_app.logger.error(f"API error during report upload: {e}")
        return None
    except FileNotFoundError:
        current_app.logger.error(f"File not found: {file_path}")
        return None


def download_report(report_id: int, save_path: str):
    """Download a report by report ID."""
    url = f"{current_app.config['API_BASE_URL']}/reports/{report_id}/download"
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        return True  # Successfully downloaded
    except requests.RequestException as e:
        current_app.logger.error(f"API error during report download: {e}")
        return False


def upload_supplemental_material(patient_id: int, file_path: str):
    """Upload supplemental material for a specific patient."""
    url = f"{current_app.config['API_BASE_URL']}/suppleMat"
    file_name = os.path.basename(file_path)
    try:
        with open(file_path, "rb") as file:
            files = {"file": (file_name, file)}
            data = {"patient_id": patient_id}
            response = requests.post(url, files=files, data=data, timeout=10)
            response.raise_for_status()
            return response.json()  # Return the response from the backend
    except requests.RequestException as e:
        current_app.logger.error(
            f"API error during supplemental material upload: {e}"
        )
        return None
    except FileNotFoundError:
        current_app.logger.error(f"File not found: {file_path}")
        return None


def download_supplemental_material(material_id: int, save_path: str):
    """Download supplemental material by its ID."""
    url = f"{current_app.config['API_BASE_URL']}/suppleMat/{material_id}/download"
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        return True  # Successfully downloaded
    except requests.RequestException as e:
        current_app.logger.error(
            f"API error during supplemental material download: {e}"
        )
        return False


def fetch_reports_for_patient(patient_id: int):
    """Fetch all reports for a specific patient."""
    url = f"{current_app.config['API_BASE_URL']}/patients/{patient_id}/reports"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()  # Return the list of reports
    except requests.RequestException as e:
        current_app.logger.error(f"API error while fetching reports: {e}")
        return []


def fetch_supplemental_materials_for_patient(patient_id: int):
    """Fetch all supplemental materials for a specific patient."""
    url = f"{current_app.config['API_BASE_URL']}/patients/{patient_id}/supplemental_materials"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()  # Return the list of supplemental materials
    except requests.RequestException as e:
        current_app.logger.error(
            f"API error while fetching supplemental materials: {e}"
        )
        return []
