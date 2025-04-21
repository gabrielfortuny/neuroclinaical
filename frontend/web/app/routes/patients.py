"""Patient routes."""

from flask import (
    request,
    redirect,
    url_for,
    Blueprint,
    abort,
    render_template,
    flash,
    send_file,
)
from app.services.patients_api import (
    fetch_a_patient,
    create_new_patient,
    upload_report,
    download_report,
    upload_supplemental_material,
    download_supplemental_material,
    fetch_reports_for_patient,
    fetch_supplemental_materials_for_patient,
)

bp = Blueprint("patient", __name__, url_prefix="/patients")


@bp.route("/<int:patient_id>", methods=["GET", "POST"])
def patient_detail(patient_id):
    """Render patient detail page with patient data."""
    patient = fetch_a_patient(patient_id)
    if not patient:
        abort(404)

    # Fetch reports and supplemental materials for the patient
    reports = fetch_reports_for_patient(patient_id)
    supplemental_materials = fetch_supplemental_materials_for_patient(
        patient_id
    )

    return render_template(
        "patient/detail.html",
        patient=patient,
        reports=reports,
        supplemental_materials=supplemental_materials,
    )


@bp.route("/create", methods=["GET", "POST"])
def create_patient():
    """Create a new patient."""
    if request.method == "POST":
        name = request.form.get("name")
        if name:
            create_new_patient(name)
            return redirect(url_for("dashboard.dashboard_home"))
    return render_template("patient/create.html")


@bp.route("/<int:patient_id>/upload_report", methods=["POST"])
def upload_patient_report(patient_id):
    """Upload a report for a specific patient."""
    if "file" not in request.files:
        flash("No file part in the request.", "error")
        return redirect(
            url_for("patient.patient_detail", patient_id=patient_id)
        )

    file = request.files["file"]
    if file.filename == "":
        flash("No selected file.", "error")
        return redirect(
            url_for("patient.patient_detail", patient_id=patient_id)
        )

    save_path = f"/tmp/{file.filename}"  # Temporary save path
    file.save(save_path)

    response = upload_report(patient_id, save_path)
    if response:
        flash("Report uploaded successfully.", "success")
    else:
        flash("Failed to upload report.", "error")

    return redirect(url_for("patient.patient_detail", patient_id=patient_id))


@bp.route("/reports/<int:report_id>/download", methods=["GET"])
def download_patient_report(report_id):
    """Download a report by its ID."""
    save_path = f"/tmp/report_{report_id}.pdf"  # Temporary save path
    success = download_report(report_id, save_path)
    if success:
        return send_file(save_path, as_attachment=True)
    else:
        flash("Failed to download report.", "error")
        return redirect(
            url_for("patient.patient_detail", patient_id=report_id)
        )


@bp.route("/<int:patient_id>/upload_supplemental", methods=["POST"])
def upload_patient_supplemental(patient_id):
    """Upload supplemental material for a specific patient."""
    if "file" not in request.files:
        flash("No file part in the request.", "error")
        return redirect(
            url_for("patient.patient_detail", patient_id=patient_id)
        )

    file = request.files["file"]
    if file.filename == "":
        flash("No selected file.", "error")
        return redirect(
            url_for("patient.patient_detail", patient_id=patient_id)
        )

    save_path = f"/tmp/{file.filename}"  # Temporary save path
    file.save(save_path)

    response = upload_supplemental_material(patient_id, save_path)
    if response:
        flash("Supplemental material uploaded successfully.", "success")
    else:
        flash("Failed to upload supplemental material.", "error")

    return redirect(url_for("patient.patient_detail", patient_id=patient_id))


@bp.route("/supplemental/<int:material_id>/download", methods=["GET"])
def download_patient_supplemental(material_id):
    """Download supplemental material by its ID."""
    save_path = f"/tmp/supplemental_{material_id}.pdf"  # Temporary save path
    success = download_supplemental_material(material_id, save_path)
    if success:
        return send_file(save_path, as_attachment=True)
    else:
        flash("Failed to download supplemental material.", "error")
        return redirect(
            url_for("patient.patient_detail", patient_id=material_id)
        )
