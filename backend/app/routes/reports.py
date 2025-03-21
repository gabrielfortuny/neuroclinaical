from flask import Blueprint, jsonify
from flask_jwt_extended import current_user, jwt_required
from flask_restful import Api, Resource
from backend.app.__init__ import db
from backend.app.models import Report

<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
reports_bp = Blueprint("reports", __name__, url_prefix="/reports")
=======
reports_bp = Blueprint("reports", __name__)
>>>>>>> Stashed changes
=======
reports_bp = Blueprint("reports", __name__)
>>>>>>> Stashed changes
=======
reports_bp = Blueprint("reports", __name__)
>>>>>>> Stashed changes
api = Api(reports_bp)


@reports_bp.route("", methods=["POST"])
@jwt_required()
def upload_report():
    pass
    # TODO IMPLEMENT, TOO TIRED RN
    # WROTE MOST OF ALL THE UTILITIES THAT BELONG IN HERE


@reports_bp.route("/<int:report_id>", methods=["GET"])
@jwt_required()
def get_report_metadata(report_id: int):
    user = current_user  # Ensure token is for valid user in DB
    # TODO: Change openapi.yaml to account for this
    if user is None:
        return (
            jsonify({"error": "Unauthorized: Missing or Invalid Token"}),
            401,
        )  # User is not in DB / Invalid token
    report = db.session.get(Report, report_id)
    if report is None:
        return 404  # Not a valid report ID
    return (
        jsonify(
            {
                "report_id": report.id,
                "patient_id": report.patient_id,
                "uploaded_at": report.created_at,
            }
        ),
        200,
    )


@reports_bp.route("/<int:report_id>", methods=["DELETE"])
@jwt_required()
def delete_report(report_id: int):
    user = current_user  # Ensure token is for valid user in DB
    # TODO: Change openapi.yaml to account for this
    if user is None:
        return (
            jsonify({"error": "Unauthorized: Missing or Invalid Token"}),
            401,
        )  # User is not in DB / Invalid token
    report = db.session.get(Report, report_id)
    if report is None:
        return 404  # Not a valid report ID
    db.session.delete(report)
    db.session.commit()
    return 204


@reports_bp.route("/<int:report_id>/download", methods=["GET"])
@jwt_required()
def download_report(report_id: int):
    # TODO IMPLEMENT, TOO TIRED RN
    # HAVEN'T EVEN STARTED
    pass
