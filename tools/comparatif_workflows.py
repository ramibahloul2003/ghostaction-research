import requests
import pandas as pd

# --- Étape 1 : Workflows du paper original ---
original_workflows = [
    "Initial Access", "Execution", "Persistence", "Privilege Escalation",
    "Defense Evasion", "Credential Access", "Discovery", "Lateral Movement",
    "Collection", "Exfiltration", "Impact"
]

# --- Étape 2 : Récupérer les workflows StepSecurite depuis leur site ---
# Exemple fictif si StepSecurite propose une API JSON publique
url = "https://stepsecurite.org/api/workflows"  # à adapter selon le vrai endpoint
response = requests.get(url)
step_workflows = []

if response.status_code == 200:
    data = response.json()
    # On suppose que les noms de workflows sont dans data['workflows']
    step_workflows = [wf['name'].strip() for wf in data.get('workflows', [])]
else:
    print("❌ Impossible de récupérer les workflows StepSecurite. Vérifie l'URL/API.")

# --- Étape 3 : Normalisation ---
step_workflows_lower = [wf.lower() for wf in step_workflows]
original_workflows_lower = [wf.lower() for wf in original_workflows]

# --- Étape 4 : Comparaison ---
all_workflows = list(set(step_workflows_lower + original_workflows_lower))
compare_df = pd.DataFrame({
    'Workflow': all_workflows,
    'Présent_dans_stepsecurite': [wf in step_workflows_lower for wf in all_workflows],
    'Présent_dans_paper': [wf in original_workflows_lower for wf in all_workflows]
})

# Concordance
def concordance(row):
    if row['Présent_dans_stepsecurite'] and row['Présent_dans_paper']:
        return "Identique"
    elif row['Présent_dans_stepsecurite']:
        return "Unique à StepSecurite"
    elif row['Présent_dans_paper']:
        return "Unique au paper"
    else:
        return "Erreur"

compare_df['Concordance'] = compare_df.apply(concordance, axis=1)

# --- Étape 5 : Export CSV ---
compare_df.to_csv("comparatif_stepsecurite_vs_paper.csv", index=False)
print("✅ Comparatif généré : comparatif_stepsecurite_vs_paper.csv")
