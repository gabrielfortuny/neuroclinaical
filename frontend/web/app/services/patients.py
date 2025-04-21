"""API requests for patients."""

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
