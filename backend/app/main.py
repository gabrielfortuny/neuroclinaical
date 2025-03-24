from app import create_app
from flask import jsonify, current_app
import urllib
import os
import json

app = create_app()
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
OLLAMA_URL = os.getenv("OLLAMA_HOST")


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify(status="OK", message="Service is healthy"), 200


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


@app.route("/debug/ollama", methods=["GET"])
def test_ollama():
    """Check ollama is alive"""
    payload = {"model": "mymodel", "prompt": "hi how are you", "stream": False}

    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=None) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result
    except urllib.error.URLError as e:
        print("Error contacting Ollama:", e)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
