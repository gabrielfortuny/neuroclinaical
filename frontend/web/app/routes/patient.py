from flask import Blueprint, render_template, request, current_app, flash
import requests

bp = Blueprint("patient", __name__, url_prefix="/patients")


@bp.route("/<int:patient_id>", methods=["GET", "POST"])
def patient_detail(patient_id):
    return render_template("patient/detail.html")
