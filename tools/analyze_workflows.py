import yaml
import os
import csv

# Chemin vers le dossier contenant les workflows
folder = os.path.join(os.path.dirname(__file__), "..", "collected-workflows")
output_csv = os.path.join(os.path.dirname(__file__), "..", "workflow_summary.csv")

# Préparer le CSV
with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["file", "workflow_name", "triggers", "jobs"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Parcourir tous les fichiers YAML
    for file in os.listdir(folder):
        if not (file.endswith(".yml") or file.endswith(".yaml")):
            continue

        path = os.path.abspath(os.path.join(folder, file))
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                documents = list(yaml.safe_load_all(f))  # tous les documents
        except yaml.YAMLError as e:
            print(f"{file} invalide: {e}")
            continue
        except OSError as e:
            print(f"{file} impossible à ouvrir: {e}")
            continue

        for doc_index, data in enumerate(documents):
            if not isinstance(data, dict):
                continue

            workflow_name = data.get("name", f"{file}-doc{doc_index+1}")
            triggers = data.get("on") or data.get("triggers") or "N/A"
            jobs = list(data.get("jobs", {}).keys()) if data.get("jobs") else "N/A"

            writer.writerow({
                "file": file,
                "workflow_name": workflow_name,
                "triggers": str(triggers),
                "jobs": str(jobs)
            })

print(f"✅ Analyse terminée. Résumé sauvegardé dans {output_csv}")
