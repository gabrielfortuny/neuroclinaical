from datetime import datetime
from flask import Blueprint, request, jsonify
from app.models import Patient
from app import db


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


@patients_bp.route("/<int:patient_id>/reports", methods=["GET"])
def get_patient_reports(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found."}), 404

    # Assuming a `reports` relationship on Patient
    reports = patient.reports
    data = [
        {
            "report_id": report.id,
            "uploaded_at": (
                report.uploaded_at.isoformat() if report.uploaded_at else None
            ),
        }
        for report in reports
    ]
    return jsonify(data), 200


@patients_bp.route("/<int:patient_id>/seizures", methods=["GET"])
def get_seizures_by_patient(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found."}), 404

    # Assuming a `seizures` relationship on Patient, with nested `electrodes`
    data = []
    for seizure in patient.seizures:
        seizure_data = {
            "id": seizure.id,
            "day": seizure.day,
            "start_time": (
                seizure.start_time.strftime("%H:%M:%S") if seizure.start_time else None
            ),
            "duration": seizure.duration,  # Already in ISO 8601 format
            "created_at": (
                seizure.created_at.isoformat() if seizure.created_at else None
            ),
            "modified_at": (
                seizure.modified_at.isoformat() if seizure.modified_at else None
            ),
            "electrodes": [
                {
                    "id": e.id,
                    "name": e.name,
                    "created_at": e.created_at.isoformat() if e.created_at else None,
                    "modified_at": e.modified_at.isoformat() if e.modified_at else None,
                }
                for e in seizure.electrodes
            ],
        }
        data.append(seizure_data)

    return jsonify(data), 200


@patients_bp.route("/<int:patient_id>/supplemental_materials", methods=["GET"])
def get_patient_supplemental_materials(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found."}), 404

    # Assuming a `supplemental_materials` relationship on Patient
    data = [
        {
            "id": material.id,
            "filepath": material.filepath,
            "created_at": (
                material.created_at.isoformat() if material.created_at else None
            ),
        }
        for material in patient.supplemental_materials
    ]
    return jsonify(data), 200


@patients_bp.route("/<int:patient_id>/drug_administration", methods=["GET"])
def get_patient_drug_administration(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found."}), 404

    # Assuming patient.drug_administrations exists and each record links to a Drug model
    data = []
    for record in patient.drug_administrations:
        data.append(
            {
                "id": record.id,
                "drug_id": record.drug_id,
                "drug_name": record.drug.name if record.drug else None,
                "drug_class": record.drug.drug_class if record.drug else None,
                "day": record.day,
                "dosage": record.dosage,
                "time": record.time.strftime("%H:%M:%S") if record.time else None,
            }
        )

    return jsonify(data), 200
