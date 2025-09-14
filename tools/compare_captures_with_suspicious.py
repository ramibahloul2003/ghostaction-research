"""
Compare les captures issues de la simulation (simulation/captures_summary.csv)
avec la liste des workflows suspects (workflow_suspicious.csv).

Génère analysis/capture_vs_static_match.csv avec :
 - file_suspicious : nom de fichier YAML suspect (depuis workflow_suspicious.csv)
 - workflow_capture  : nom du workflow reçu dans les captures (captures_summary.csv)
 - match_type : "Exact", "Normalized", "NoMatch"
 - details : infos supplémentaires (secret, timestamp, filepath capture)
"""

import pandas as pd
import re
from pathlib import Path
from difflib import SequenceMatcher

# chemins
SUSP_CSV = Path("workflow_suspicious.csv")
CAPS_CSV = Path("simulation/captures_summary.csv")
OUT_DIR = Path("analysis")
OUT_DIR.mkdir(exist_ok=True)
OUT_CSV = OUT_DIR / "capture_vs_static_match.csv"

def normalize_name(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = s.lower()
    # enlever extension .yml .yaml et préfixes .github_workflows_ ou out_ etc.
    s = re.sub(r'\.github[_-]?workflows[_-]?', '', s)
    s = re.sub(r'\.yml|\.yaml', '', s)
    # remplacer caractères non alphanum par underscore
    s = re.sub(r'[^a-z0-9]+', '_', s).strip('_')
    return s

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# --- charger ---
if not SUSP_CSV.exists():
    raise SystemExit(f"❌ Fichier introuvable: {SUSP_CSV}")
if not CAPS_CSV.exists():
    raise SystemExit(f"❌ Fichier introuvable: {CAPS_CSV}")

susp = pd.read_csv(SUSP_CSV)
caps = pd.read_csv(CAPS_CSV)

# colonnes attendues :
# susp doit contenir "file" (ou "workflow_name") - on va chercher 'file' sinon 'workflow_name'
if 'file' not in susp.columns and 'workflow_name' in susp.columns:
    susp = susp.rename(columns={'workflow_name': 'file'})

# caps attendu : 'workflow','file','received_at','secret' etc.
if 'workflow' not in caps.columns and 'workflow_name' in caps.columns:
    caps = caps.rename(columns={'workflow_name': 'workflow'})

# normaliser noms
susp['file_norm'] = susp['file'].astype(str).apply(normalize_name)
caps['workflow_norm'] = caps['workflow'].astype(str).apply(normalize_name)

rows = []
# indexer caps par workflow_norm pour lookup rapide
caps_by_norm = {}
for i, r in caps.iterrows():
    caps_by_norm.setdefault(r['workflow_norm'], []).append(r.to_dict())

# pour chaque suspicious workflow, chercher une correspondance
for i, r in susp.iterrows():
    file_orig = r['file']
    file_norm = normalize_name(str(file_orig))
    matched = False

    # 1) match exact (normalized)
    if file_norm in caps_by_norm:
        for c in caps_by_norm[file_norm]:
            rows.append({
                'file_suspicious': file_orig,
                'file_norm': file_norm,
                'workflow_capture': c.get('workflow'),
                'workflow_norm': c.get('workflow_norm'),
                'received_at': c.get('received_at', ''),
                'secret': c.get('secret', ''),
                'match_type': 'Exact',
                'details': f"capture_file={c.get('file','')}"
            })
        matched = True
        continue

    # 2) fuzzy match: chercher la meilleure similarité contre toutes captures
    best = ('', 0.0, None)
    for norm, clist in caps_by_norm.items():
        score = similar(file_norm, norm)
        if score > best[1]:
            best = (norm, score, clist)
    # seuil fuzzy (ajustable)
    if best[1] >= 0.75:
        # ajouter toutes les captures pour ce norm
        for c in best[2]:
            rows.append({
                'file_suspicious': file_orig,
                'file_norm': file_norm,
                'workflow_capture': c.get('workflow'),
                'workflow_norm': c.get('workflow_norm'),
                'received_at': c.get('received_at', ''),
                'secret': c.get('secret', ''),
                'match_type': f'Fuzzy({best[1]:.2f})',
                'details': f"matched_norm={best[0]}, capture_file={c.get('file','')}"
            })
        matched = True

    if not matched:
        rows.append({
            'file_suspicious': file_orig,
            'file_norm': file_norm,
            'workflow_capture': '',
            'workflow_norm': '',
            'received_at': '',
            'secret': '',
            'match_type': 'NoMatch',
            'details': ''
        })

# sauver
df_out = pd.DataFrame(rows)
df_out.to_csv(OUT_CSV, index=False, encoding="utf-8")
print(f"✅ Comparatif généré : {OUT_CSV} (lignes: {len(df_out)})")
