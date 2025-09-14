import os
import requests
import base64
import csv
from dotenv import load_dotenv

# -----------------------------
# 1️⃣ Charger le token GitHub
# -----------------------------
load_dotenv()  # lit le fichier .env
TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise Exception("Erreur : token non trouvé !")
print("✅ Token chargé avec succès !")

HEADERS = {"Authorization": f"token {TOKEN}"}

# -----------------------------
# 2️⃣ Paramètres de recherche
# -----------------------------
# Mots-clés pour rechercher les workflows suspects
SEARCH_KEYWORDS = [
    "curl",
    "wget",
    "${{ secrets."
]

# Extension des fichiers
EXTENSION = "yml"

# Dossier pour sauvegarder les fichiers YAML
COLLECT_DIR = os.path.join(os.getcwd(), "collected-workflows")
os.makedirs(COLLECT_DIR, exist_ok=True)

# Fichier CSV pour les métadonnées
INDEX_FILE = os.path.join(os.getcwd(), "index.csv")
if not os.path.exists(INDEX_FILE):
    with open(INDEX_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["repo", "path", "sha"])

# -----------------------------
# 3️⃣ Fonction pour chercher les fichiers
# -----------------------------
def search_github(keyword, page=1):
    url = f"https://api.github.com/search/code?q={keyword}+extension:{EXTENSION}&per_page=100&page={page}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"⚠️ Erreur GitHub API {response.status_code} pour le mot-clé: {keyword}")
        return []
    data = response.json()
    return data.get("items", [])

# -----------------------------
# 4️⃣ Fonction pour récupérer le contenu YAML
# -----------------------------
def fetch_yaml(repo_full_name, path):
    url = f"https://api.github.com/repos/{repo_full_name}/contents/{path}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"⚠️ Impossible de récupérer {repo_full_name}/{path}")
        return None
    data = response.json()
    content = base64.b64decode(data["content"]).decode()
    return content, data["sha"]

# -----------------------------
# 5️⃣ Collecte et sauvegarde
# -----------------------------
for keyword in SEARCH_KEYWORDS:
    print(f"🔍 Recherche pour : {keyword}")
    items = search_github(keyword)
    for item in items:
        repo = item["repository"]["full_name"]
        path = item["path"]

        yaml_content, sha = fetch_yaml(repo, path)
        if yaml_content is None:
            continue

        # Sauvegarder le fichier YAML
        file_name = path.replace("/", "_")
        file_path = os.path.join(COLLECT_DIR, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(yaml_content)
        print(f"✅ {file_name} sauvegardé !")

        # Sauvegarder les métadonnées dans index.csv
        with open(INDEX_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([repo, path, sha])
