from flask import Blueprint, jsonify, abort
from flask_restful import Api, Resource
from app import db
from app.models import Seizure

seizures_bp = Blueprint("seizures", __name__, url_prefix="/seizures")
api = Api(seizures_bp)


@seizures_bp.route("/<int:seizure_id>", methods=["GET"])
def get_seizure(seizure_id: int):
    """
    Retrieves detailed information about a specific seizure by ID,
    including related electrodes.
    """
    seizure = db.session.get(Seizure, seizure_id)

    if seizure is None:
        abort(404)

    result = jsonify(
        {
            "id": seizure.id,
            "patient_id": seizure.patient_id,
            "day": seizure.day,
            "start_time": seizure.start_time,
            "duration": seizure.duration,
            "electrodes": [],  # TODO
        }
    )

    return result, 200
