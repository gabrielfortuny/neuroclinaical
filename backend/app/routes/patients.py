from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from app.models import Patient
from app import db
from app.services.create_graphs.create_graphs import make_plot2
from io import BytesIO
from PIL import Image
from app.services.create_graphs.generate_graphs import get_graphs


patients_bp = Blueprint("patients", __name__, url_prefix="/patients")


@patients_bp.route("", methods=["GET"])
def get_all_patients():
    patients = Patient.query.all()
    data = [{"id": p.id, "name": p.name} for p in patients]
    return jsonify(data), 200


@patients_bp.route("", methods=["POST"])
def create_patient():
    data = request.get_json()
    name = data.get("name")

    if not name:
        return jsonify({"error": "Invalid input: 'name' is required."}), 400

    patient = Patient(name=name)
    db.session.add(patient)
    db.session.commit()

    return (
        jsonify(
            {
                "id": patient.id,
                "name": patient.name,
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
                # "dob": patient.dob.isoformat() if patient.dob else None,
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
            return (
                jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}),
                400,
            )

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
    patient = db.session.get(Patient, patient_id)
    if not patient:
        return jsonify({"error": "Patient not found."}), 404

    db.session.delete(patient)
    db.session.commit()
    return "", 204


@patients_bp.route("/<int:patient_id>/reports", methods=["GET"])
def get_patient_reports(patient_id):
    # Import db only
    from app import db

    # Check if patient exists
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found."}), 404

    # Use SQLAlchemy's text function to query reports directly
    from sqlalchemy import text

    try:
        # Execute raw SQL query to get reports for the patient
        result = db.session.execute(
            text(
                "SELECT id, patient_id, summary, file_path, file_name FROM reports WHERE patient_id = :patient_id"
            ),
            {"patient_id": patient_id},
        )

        # Convert row objects to dictionaries
        data = []
        for row in result:
            report_dict = {
                "report_id": row.id,
                "patient_id": row.patient_id,
                "summary": row.summary,
                "file_path": row.file_path,
                "file_name": row.file_name,
            }
            data.append(report_dict)

        return jsonify(data), 200

    except Exception as e:
        from flask import current_app

        current_app.logger.error(f"Error retrieving patient reports: {str(e)}")
        return jsonify({"error": "Failed to retrieve reports"}), 500


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
                seizure.start_time.strftime("%H:%M:%S")
                if seizure.start_time
                else None
            ),
            "duration": seizure.duration,  # Already in ISO 8601 format
            "electrodes": [
                {
                    "id": e.id,
                    "name": e.name
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
            "file_path": material.file_path,
        }
        for material in patient.supplemental_materials
    ]
    return jsonify(data), 200


@patients_bp.route(
    "/<int:patient_id>/graph/<int:graph_number>", methods=["GET"]
)
def get_patient_graph(patient_id, graph_number):
    """Graph number is 0 - 8"""
    try:
        graph_image = get_graphs(patient_id, graph_number)

        # Save to in-memory buffer
        img_io = BytesIO()
        graph_image.save(img_io, "PNG")
        img_io.seek(0)

        return send_file(img_io, mimetype="image/png", as_attachment=False)

    except Exception as e:
        return {"error": str(e)}, 500


@patients_bp.route("/<int:patient_id>/drug_administration", methods=["GET"])
def get_patient_drug_administration(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found."}), 404

    # Import psycopg2 for direct database access
    import psycopg2
    import psycopg2.extras

    try:
        # Get database connection parameters from the environment
        host = "db"  # Container name from docker-compose
        port = 5432  # Default PostgreSQL port
        user = "postgres"
        password = "password"
        database = "neuroclinaical"

        # Create direct connection to PostgreSQL
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
        )
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Get drug administrations with drug information - removed the time column
        cursor.execute(
            """
            SELECT 
                da.id, 
                d.name AS drug_name, 
                da.day, 
                da.dosage,
                da.time
            FROM 
                drug_administration da
            WHERE 
                da.patient_id = %s
            ORDER BY 
                da.day ASC
        """,
            (patient_id,),
        )

        # Fetch all results
        drugs = cursor.fetchall()

        # Convert to list of dictionaries for JSON response
        result = []
        for drug in drugs:
            drug_data = {
                "id": drug["id"],
                "drug_name": drug["drug_name"],
                "drug_class": drug["drug_class"],
                "day": drug["day"],
                "dosage": drug["dosage"],
                "time": drug[
                    "time"
                ],  # Since the time column doesn't exist in your database
            }
            result.append(drug_data)

        # Close the database connection
        cursor.close()
        conn.close()

        return jsonify(result), 200

    except Exception as e:
        # current_app.logger.error(f"Error retrieving drug administrations: {str(e)}")
        import traceback

        # current_app.logger.error(traceback.format_exc())
        return (
            jsonify({"error": "Failed to retrieve drug administrations"}),
            500,
        )
