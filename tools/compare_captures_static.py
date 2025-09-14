# tools/compare_captures_static_mapped.py
import csv
import json
from pathlib import Path

# Chemins
CAPTURE_DIR = Path("./simulation/capture-server/captures")
STATIC_CSV = Path("./workflow_suspicious.csv")
OUTPUT_CSV = Path("./analysis/capture_vs_static_match.csv")

# Lire les workflows statiques
static_workflows = {}
with open(STATIC_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        static_workflows[row["workflow_name"]] = row  # clé = workflow_name réel

# Mapping des noms simulés → noms réels
sim_to_real = {
    "linters_sim": "Linters",
    "nightly-build_sim": "Nightly Build",
    "publish_sim": "Publish",
    "langflow-nightly-build_sim": "Langflow Nightly Build",
    "daily-checks-for-appcodeecommerce121_sim": "Daily Checks for appcodeEcommerce121",
    "diffreport_sim": "DiffReport",
    "ci_sim": "CI",
}

# Champs CSV de sortie
OUTPUT_FIELDS = [
    "file_suspicious", "file_norm", "workflow_capture", "workflow_norm",
    "received_at", "secret", "match_type", "details"
]

rows_out = []

# Parcourir les captures
for cap_file in CAPTURE_DIR.glob("*.json"):
    with open(cap_file, encoding="utf-8") as f:
        payload = json.load(f)

    workflow_sim = payload.get("json", {}).get("workflow", "")
    workflow_name = sim_to_real.get(workflow_sim, workflow_sim)  # mapping
    secret = payload.get("json", {}).get("secret", "")
    received_at = payload.get("received_at", "")

    match_type = "NoMatch"
    details = ""

    if workflow_name in static_workflows:
        match_type = "Match"
        details = f"Secret captured: {secret}"

    # Ajouter ligne CSV
    rows_out.append({
        "file_suspicious": workflow_sim + ".yml",
        "file_norm": workflow_name + ".yml",
        "workflow_capture": workflow_sim,
        "workflow_norm": workflow_name,
        "received_at": received_at,
        "secret": secret,
        "match_type": match_type,
        "details": details
    })

# Créer dossier analysis si nécessaire
OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

# Écrire CSV
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
    writer.writeheader()
    writer.writerows(rows_out)

print(f"✅ Comparatif généré : {OUTPUT_CSV} (lignes: {len(rows_out)})")
