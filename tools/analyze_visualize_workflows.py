import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import ast
import yaml
import os

WORKFLOW_FOLDER = "collected-workflows"
CSV_FILE = "workflow_summary.csv"
SUSPICIOUS_CSV = "workflow_suspicious.csv"

# 🔹 1. Charger le CSV existant
df = pd.read_csv(CSV_FILE)

print("Aperçu initial des données :")
print(df.head())

# 🔹 2. Nettoyage et transformation
list_columns = ['triggers', 'jobs', 'secrets']
for col in list_columns:
    if col in df.columns:
        df[col] = df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else (x if isinstance(x, list) else []))

df['workflow_name'] = df['workflow_name'].str.replace(r'[^\w\s]', '', regex=True)
df['num_jobs'] = df['jobs'].apply(len)
df['num_secrets'] = df['secrets'].apply(len)

# 🔹 3. Détection de workflows suspects
# Considère comme suspect si au moins 1 secret et plus de 2 jobs
df['suspicious'] = df.apply(lambda row: row['num_secrets'] > 0 and row['num_jobs'] > 2, axis=1)

# Export des workflows suspects
df_suspicious = df[df['suspicious']]
df_suspicious.to_csv(SUSPICIOUS_CSV, index=False)
print(f"✅ {len(df_suspicious)} workflows suspects exportés vers {SUSPICIOUS_CSV}")

# 🔹 4. Visualisations
sns.set(style="whitegrid")

# Histogramme du nombre de jobs
plt.figure(figsize=(10,6))
sns.histplot(df['num_jobs'], bins=20, kde=False, color='skyblue')
plt.title("Distribution du nombre de jobs par workflow")
plt.xlabel("Nombre de jobs")
plt.ylabel("Nombre de workflows")
plt.show()

# Histogramme du nombre de secrets
plt.figure(figsize=(10,6))
sns.histplot(df['num_secrets'], bins=20, kde=False, color='salmon')
plt.title("Distribution du nombre de secrets par workflow")
plt.xlabel("Nombre de secrets")
plt.ylabel("Nombre de workflows")
plt.show()

# Scatter plot : jobs vs secrets
plt.figure(figsize=(10,6))
sns.scatterplot(data=df, x='num_jobs', y='num_secrets', hue='suspicious', palette={True:'red', False:'blue'})
plt.title("Nombre de jobs vs Nombre de secrets")
plt.xlabel("Nombre de jobs")
plt.ylabel("Nombre de secrets")
plt.show()

# Top 10 triggers
triggers_flat = [item for sublist in df['triggers'] for item in sublist]
trigger_counts = pd.Series(triggers_flat).value_counts()
plt.figure(figsize=(10,6))
sns.barplot(x=trigger_counts.head(10).values, y=trigger_counts.head(10).index, palette='viridis')
plt.title("Top 10 triggers")
plt.xlabel("Nombre d'apparitions")
plt.ylabel("Trigger")
plt.show()

# Heatmap : triggers vs nombre de secrets (simplifiée)
top_triggers = trigger_counts.head(10).index
heatmap_data = pd.DataFrame(0, index=df['workflow_name'], columns=top_triggers)
for idx, row in df.iterrows():
    for trig in row['triggers']:
        if trig in top_triggers:
            heatmap_data.loc[row['workflow_name'], trig] = row['num_secrets']

plt.figure(figsize=(12,8))
sns.heatmap(heatmap_data[top_triggers], cmap="Reds", cbar_kws={'label': 'Nombre de secrets'})
plt.title("Heatmap : Top triggers vs nombre de secrets par workflow")
plt.xlabel("Trigger")
plt.ylabel("Workflow")
plt.show()

print("\nAnalyse complète avec détection des workflows suspects terminée ! ✅")
