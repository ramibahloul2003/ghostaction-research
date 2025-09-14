# simulation/capture-server/server.py
from flask import Flask, request, jsonify
from pathlib import Path
from datetime import datetime
import uuid
import json
import os

BASE_DIR = Path(__file__).resolve().parent
CAP_DIR = BASE_DIR / "captures"
CAP_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)

def save_capture(payload: dict):
    # filename unique : timestamp_uuid.json
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    fname = f"capture_{ts}_{uuid.uuid4().hex[:8]}.json"
    path = CAP_DIR / fname
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return str(path)

@app.route("/collect", methods=["POST"])
def collect():
    try:
        remote = request.remote_addr or ""
        headers = dict(request.headers)
        raw_body = request.get_data(as_text=True)

        # try parse JSON body if it is JSON
        body_json = None
        try:
            body_json = request.get_json(silent=True)
        except Exception:
            body_json = None

        payload = {
            "received_at": datetime.utcnow().isoformat() + "Z",
            "remote_addr": remote,
            "headers": headers,
            "body": raw_body,
            "json": body_json
        }

        saved = save_capture(payload)
        app.logger.info(f"Captured POST from {remote} -> {saved}")
        return jsonify({"status": "ok", "saved": saved}), 200
    except Exception as e:
        app.logger.exception("Error handling collect")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route("/", methods=["GET"])
def hello():
    return (
        "Capture server (simulation). POST to /collect to save payloads.\n"
        f"Saved captures: {len(list(CAP_DIR.glob('capture_*.json')))}"
    )

if __name__ == "__main__":
    # production: host 0.0.0.0 to be reachable from Docker/act containers
    # debug False for safer runs
    app.run(host="127.0.0.1", port=5000, debug=False)

