# tools/aggreg_captures.py
import json
import csv
from pathlib import Path

CAP_DIR = Path("simulation/capture-server/captures")
OUT_CSV = Path("simulation/captures_summary.csv")

files = sorted(CAP_DIR.glob("capture_*.json"))
rows = []
for f in files:
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
        body = d.get("json") or {}
        rows.append({
            "file": f.name,
            "received_at": d.get("received_at"),
            "remote_addr": d.get("remote_addr"),
            "workflow": body.get("workflow"),
            "secret": body.get("secret"),
            "user_agent": d.get("headers", {}).get("User-Agent", ""),
            "content_length": d.get("headers", {}).get("Content-Length", "")
        })
    except Exception as e:
        print(f"Erreur lecture {f}: {e}")

if rows:
    with OUT_CSV.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"✅ {len(rows)} captures agrégées -> {OUT_CSV}")
else:
    print("Aucune capture trouvée.")
