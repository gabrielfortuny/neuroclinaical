from app import create_app
from flask import jsonify, current_app


app = create_app()


@app.route("/hello", methods=["GET"])
def hello():
    return jsonify({"message": "Hello World"})


print("\n=== REGISTERED ROUTES ===\n")
with app.app_context():
    for rule in app.url_map.iter_rules():
        methods = ",".join(
            method for method in rule.methods if method not in ["HEAD", "OPTIONS"]
        )
        print(f"Path: {rule} → Endpoint: {rule.endpoint} → Methods: {methods}")


@app.route("/debug/routes", methods=["GET"])
def list_routes():
    """List all registered routes with endpoints and methods"""
    routes = []
    for rule in current_app.url_map.iter_rules():
        # Exclude the static and debug routes themselves
        if "static" not in rule.endpoint and "debug" not in rule.endpoint:
            methods = ",".join(
                method for method in rule.methods if method not in ["HEAD", "OPTIONS"]
            )
            routes.append(
                {"endpoint": rule.endpoint, "methods": methods, "path": str(rule)}
            )

    # Sort routes by path for easier readability
    return jsonify(sorted(routes, key=lambda x: x["path"]))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
