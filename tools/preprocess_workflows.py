import yaml
import os

folder = os.path.join(os.path.dirname(__file__), "..", "collected-workflows")

for file in os.listdir(folder):
    if file.endswith(".yml") or file.endswith(".yaml"):
        path = os.path.join(folder, file)
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
                print(f"{file} est un YAML valide.")
            except yaml.YAMLError as e:
                print(f"{file} est invalide: {e}")
