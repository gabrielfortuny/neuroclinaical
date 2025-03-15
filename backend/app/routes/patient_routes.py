from flask import Blueprint
from flask_restful import Api, Resource

patient_bp = Blueprint("patients", __name__)
api = Api(patient_bp)


class PatientResource(Resource):
    def get(self):
        return {"message": "List of patients"}

    def post(self):
        return {"message": "Patient created"}, 201


api.add_resource(PatientResource, "/")
