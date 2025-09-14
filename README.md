# GhostAction Research

**Objectif**  
Analyser et reproduire de façon contrôlée la campagne **GhostAction** (vol de secrets via des workflows GitHub malicieux).

>  Toutes les expérimentations sont réalisées **en local** et **avec des secrets factices** pour des raisons de sécurité. Ne jamais utiliser de vrais secrets.

## Structure du dépôt

- 'collected-workflows/' : exemples de fichiers YAML récupérés depuis GitHub (workflows collectés).
- 'tools/' : scripts pour collecter, prétraiter, analyser et visualiser des workflows (ex : 'collect_workflows.py', 'preprocess_workflows.py', 'analyze_workflows.py', 'generate_simulated_workflows.py', 'analyze_visualize_workflows.py', 'compare_captures_static.py').
- 'simulation/' : environnement de test local
  - 'capture-server/' : petit serveur Flask qui reçoit les POSTs de simulation ('server.py') et stocke les captures dans 'captures/'.
- '.github/workflows/' : workflows simulés ('ci_simulated1..7.yml') utilisés pour la simulation.
- 'analysis/' : sorties d'analyse (ex : 'capture_vs_static_match.csv').
- 'reports/' : rapport d'expérience, observations et recommandations.
- '.env' : variables locales ( 'GITHUB_TOKEN') 
- 'index.csv et workflow_summary.csv' : résumé tabulaire des workflows trouvés sur GitHub.
- 'README.md' : ce fichier.

## Résumé du flux de travail (ce que j'ai réalisé)

1. **Collecte** : utilisation d'un script pour rechercher et télécharger des fichiers YAML depuis GitHub selon des motifs (curl, wget, '${{ secrets.' etc.) et sauvegarde dans 'collected-workflows/'.
2. **Prétraitement** : nettoyage/normalisation des YAML et création d'un index.CSV ('workflow_summary.csv') avec métadonnées (fichier, repo, jobs, triggers, références à des secrets).
3. **Analyse statique** : détection de motifs d'exfiltration (curl/wget, accès à '${{ secrets.* }}', utilisation d'actions suspectes) et génération de 'workflow_suspicious.csv'.
4. **Génération de workflows simulés** : création automatique de 7 workflows 'ci_simulated*.yml' reprenant la logique observée mais utilisant des **secrets factices** et pointant vers un serveur de capture local.
5. **Simulation & capture** : lancement d'un serveur Flask local ('simulation/capture-server/server.py') qui enregistre les POSTs reçus dans 'captures/'. Exécution des simulations (via 'act' si Docker disponible, ou via scripts PowerShell/cURL) pour produire des captures JSON.
6. **Comparaison** : scripts pour comparer captures effectives ↔ artefacts statiques et produire un CSV final d'analyse ('analysis/capture_vs_static_match.csv').
7. **Visualisation et rapport** : scripts d'analyse (pandas / matplotlib) et rédaction d'un rapport détaillé.

## Exemples de commandes

Lancer le serveur de capture :
'''bash
cd simulation/capture-server
python server.py
# Serveur écoute sur http://127.0.0.1:5000
