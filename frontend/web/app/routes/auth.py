from flask import Blueprint, render_template

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["GET", "POST"])
def login():
    # if request.method == "POST":
    #     email = request.form["email"]
    #     password = request.form["password"]
    #     # TODO: send login request to backend API
    #     flash("Logged in (stub)")
    #     return redirect(url_for("dashboard.dashboard_home"))
    return render_template("auth/login.html")


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    # if request.method == "POST":
    #     email = request.form["email"]
    #     password = request.form["password"]
    #     # TODO: send signup request to backend API
    #     flash("Signed up (stub)")
    #     return redirect(url_for("auth.login"))
    return render_template("auth/signup.html")
