from flask import Blueprint, request, jsonify
from models import Patient
from extensions import db
from datetime import datetime

patients_bp = Blueprint("patients", __name__, url_prefix="/patients")


@patients_bp.route("", methods=["GET"])
def get_all_patients():
    patients = Patient.query.all()
    data = [
        {"id": p.id, "name": p.name, "dob": p.dob.isoformat() if p.dob else None}
        for p in patients
    ]
    return jsonify(data), 200


@patients_bp.route("", methods=["POST"])
def create_patient():
    data = request.get_json()
    name = data.get("name")
    dob_str = data.get("dob")

    if not name:
        return jsonify({"error": "Invalid input: 'name' is required."}), 400

    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date() if dob_str else None
    except ValueError:
        return jsonify({"error": "Invalid input: 'dob' must be YYYY-MM-DD."}), 400

    patient = Patient(name=name, dob=dob)
    db.session.add(patient)
    db.session.commit()

    return (
        jsonify(
            {
                "id": patient.id,
                "name": patient.name,
                "dob": patient.dob.isoformat() if patient.dob else None,
            }
        ),
        201,
    )


@patients_bp.route("/<int:patient_id>", methods=["GET"])
def get_patient(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found."}), 404

    return (
        jsonify(
            {
                "id": patient.id,
                "name": patient.name,
                "dob": patient.dob.isoformat() if patient.dob else None,
            }
        ),
        200,
    )


@patients_bp.route("/<int:patient_id>", methods=["PATCH"])
def update_patient(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found."}), 404

    data = request.get_json()

    if "name" in data:
        patient.name = data["name"]
    if "dob" in data:
        try:
            patient.dob = datetime.strptime(data["dob"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    db.session.commit()

    return (
        jsonify(
            {
                "id": patient.id,
                "name": patient.name,
                "dob": patient.dob.isoformat() if patient.dob else None,
            }
        ),
        200,
    )


@patients_bp.route("/<int:patient_id>", methods=["DELETE"])
def delete_patient(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found."}), 404

    db.session.delete(patient)
    db.session.commit()
    return "", 204
