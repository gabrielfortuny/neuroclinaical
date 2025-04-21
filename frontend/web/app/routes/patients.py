"""Patient routes."""

from flask import Blueprint, render_template, request, redirect, url_for
from app.services.patients import fetch_a_patient, create_new_patient

bp = Blueprint("patient", __name__, url_prefix="/patients")


@bp.route("/<int:patient_id>", methods=["GET", "POST"])
def patient_detail(patient_id):
    """Render patient detail page with patient data."""
    patient = fetch_a_patient(patient_id)
    return render_template("patient/detail.html", patient=patient)


@bp.route("/create", methods=["GET", "POST"])
def create_patient():
    """Create a new patient."""
    if request.method == "POST":
        name = request.form.get("name")
        if name:
            create_new_patient(name)
            return redirect(url_for("patient.dashboard"))
    return render_template("patient/create.html")
