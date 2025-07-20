from flask import Flask, render_template, request, redirect, jsonify
import json
import time
import os

app = Flask(__name__)

LOG_FILE = "logs.txt"
KILL_FILE = "killswitch.json"

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

    if os.path.exists(KILL_FILE):
        with open(KILL_FILE) as f:
            state = json.load(f).get("enabled", False)
    else:
        state = False

    return render_template("index.html", logs=logs, kill_switch=state)

@app.route("/toggle", methods=["POST"])
def toggle():
    enabled = request.form.get("enabled") == "on"
    with open(KILL_FILE, "w") as f:
        json.dump({"enabled": enabled}, f)
    return redirect("/")

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
            return jsonify(json.load(f))
    return jsonify({"enabled": False})