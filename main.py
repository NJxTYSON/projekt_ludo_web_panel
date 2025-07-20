from flask import Flask, render_template, request, redirect, jsonify
import json
import time
import os

app = Flask(__name__)

# Read file paths from ENV (set in Railway > Shared Variables)
LOG_FILE = os.environ.get("LOG_FILE", "logs.txt")
KILL_FILE = os.environ.get("KILL_FILE", "killswitch.json")
ACCESS_KEY = os.environ.get("ACCESS_KEY", "1234")

@app.before_request
def check_access_key():
    # Optional: protect all routes except these
    exempt_routes = ["get_kill_switch", "static"]
    if request.endpoint not in exempt_routes:
        key = request.args.get("key")
        if key != ACCESS_KEY:
            return jsonify({"error": "Unauthorized"}), 403

@app.route("/")
def panel():
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            for line in reversed(f.readlines()):
                try:
                    logs.append(json.loads(line.strip()))
                except:
                    pass

    state = False
    if os.path.exists(KILL_FILE):
        with open(KILL_FILE) as f:
            try:
                state = json.load(f).get("enabled", False)
            except:
                pass

    return render_template("index.html", logs=logs, kill_switch=state)

@app.route("/toggle", methods=["POST"])
def toggle():
    enabled = request.form.get("enabled") == "on"
    with open(KILL_FILE, "w") as f:
        json.dump({"enabled": enabled}, f)
    return redirect(f"/?key={ACCESS_KEY}")

@app.route("/log", methods=["POST"])
def log():
    data = request.get_json(force=True)
    data["server_ts"] = int(time.time())
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")
    return jsonify({"status": "logged"}), 200

@app.route("/killswitch", methods=["GET"])
def get_kill_switch():
    if os.path.exists(KILL_FILE):
        with open(KILL_FILE) as f:
            try:
                return jsonify(json.load(f))
            except:
                pass
    return jsonify({"enabled": False})
