from flask import Blueprint, render_template
from app.services.patients_api import fetch_all_patients

bp = Blueprint("dashboard", __name__, url_prefix="/")


@bp.route("/")
def dashboard_home():
    """Dashboard with all patients."""
    patients = fetch_all_patients()
    return render_template("dashboard.html", patients=patients)
