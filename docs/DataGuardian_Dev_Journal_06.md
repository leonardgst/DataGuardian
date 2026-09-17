# DataGuardian v0.6 - Guide de test

## Objectif

Ce guide permet de valider la version 0.6 de DataGuardian, notamment :

- l'installation du package en mode développement ;
- les nouvelles fonctions publiques ;
- l'export de `ValidationResult` au format JSON ;
- la génération du rapport HTML de validation ;
- les synthèses par sévérité, code et colonne ;
- les codes de sortie destinés à la CI ;
- l'absence de régression sur les fonctionnalités existantes.

---

## 1. Se placer à la racine du projet

```powershell
cd C:\Users\leongous\Documents\Projets\DataGuardian
```

Vérifier l'arborescence :

```powershell
tree /F
```

Les nouveaux fichiers suivants doivent être présents :

```text
src\dataguardian\validation_report.py
tests\test_validation_report.py
examples\validation_report_demo.py
docs\DataGuardian_Dev_Journal_06.md
```

Les fichiers suivants doivent avoir été modifiés :

```text
src\dataguardian\contracts.py
src\dataguardian\__init__.py
pyproject.toml
```

Les artefacts suivants seront créés pendant les tests fonctionnels :

```text
artifacts\validation.json
artifacts\validation_report.html
```

---

## 2. Activer l'environnement virtuel

Si l'environnement se nomme `.venv` :

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloque l'activation :

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Vérifier Python :

```powershell
python --version
Get-Command python
```

L'environnement attendu utilise Python 3.12.

---

## 3. Réinstaller DataGuardian

```powershell
python -m pip install -e ".[dev]"
```

Vérifier la version installée :

```powershell
python -c "import importlib.metadata; print(importlib.metadata.version('dataguardian'))"
```

Résultat attendu :

```text
0.6.0
```

Vérifier les nouveaux imports publics :

```powershell
python -c "from dataguardian import save_validation_json, generate_validation_html_report, validation_exit_code; print('Imports OK')"
```

Résultat attendu :

```text
Imports OK
```

Vérifier que le module chargé correspond bien au dépôt local :

```powershell
python -c "import dataguardian.validation_report as module; print(module.__file__)"
```

Le chemin affiché doit se terminer par :

```text
DataGuardian\src\dataguardian\validation_report.py
```

---

## 4. Exécuter les nouveaux tests de la v0.6

```powershell
python -m pytest tests/test_validation_report.py -v
```

Résultat attendu :

```text
0 failed
```

Version concise :

```powershell
python -m pytest tests/test_validation_report.py -q
```

Ces tests couvrent :

- les résultats valides et invalides ;
- les compteurs d'erreurs et d'avertissements ;
- les regroupements par sévérité, code et colonne ;
- la conversion du résultat en dictionnaire ;
- l'export JSON ;
- la création automatique des dossiers parents ;
- les rapports HTML valides et invalides ;
- l'échappement des contenus HTML ;
- les codes de sortie `0` et `1`.

---

## 5. Exécuter toute la suite de tests

```powershell
python -m pytest -v
```

Le critère principal est :

```text
0 failed
```

Pour arrêter au premier échec :

```powershell
python -m pytest -x -v
```

Pour afficher les variables locales en cas d'échec :

```powershell
python -m pytest -v --showlocals
```

---

## 6. Générer le contrat YAML

```powershell
python examples/contract_demo.py
```

Vérifier que le contrat existe :

```powershell
Test-Path .\artifacts\contract.yaml
```

Résultat attendu :

```text
True
```

Afficher son contenu :

```powershell
Get-Content .\artifacts\contract.yaml
```

---

## 7. Tester le flux complet de validation

```powershell
python examples/validation_report_demo.py
```

Le script doit :

1. charger `examples/dirty_customers.csv` ;
2. charger `artifacts/contract.yaml` ;
3. exécuter `validate_dataframe()` ;
4. générer `artifacts/validation.json` ;
5. générer `artifacts/validation_report.html` ;
6. afficher une synthèse dans le terminal ;
7. retourner un code de sortie.

Exemple de sortie :

```text
Validation status: INVALID
Violations: 4
Errors: 4
Warnings: 0
JSON report: ...\artifacts\validation.json
HTML report: ...\artifacts\validation_report.html
```

Le nombre exact de violations dépend du dataset et du contrat.

Vérifier immédiatement le code de sortie :

```powershell
$LASTEXITCODE
```

Interprétation :

```text
0 = dataset conforme
1 = dataset non conforme
2 = erreur technique
```

Un code `1` signifie que le programme a fonctionné, mais que le dataset ne respecte pas le contrat.

---

## 8. Contrôler les artefacts produits

### Vérifier leur existence

```powershell
Test-Path .\artifacts\validation.json
Test-Path .\artifacts\validation_report.html
```

Résultat attendu :

```text
True
True
```

### Contrôler le JSON

```powershell
$result = Get-Content .\artifacts\validation.json -Raw | ConvertFrom-Json

$result.is_valid
$result.violation_count
$result.summary.by_severity
$result.summary.by_code
$result.summary.by_column
$result.violations
```

Vérifier la cohérence entre le compteur et la liste :

```powershell
$result.violation_count -eq $result.violations.Count
```

Résultat attendu :

```text
True
```

Chaque violation doit contenir :

- `code` ;
- `severity` ;
- `column` ;
- `expected` ;
- `observed` ;
- `message`.

Les violations globales doivent avoir `column: null` dans leur détail et être regroupées sous `DATASET` dans `summary.by_column`.

### Contrôler le rapport HTML

```powershell
Start-Process .\artifacts\validation_report.html
```

Vérifier visuellement :

- le titre `DataGuardian Validation Report` ;
- le statut `VALID` ou `INVALID` ;
- le nombre total de violations ;
- les compteurs d'erreurs et d'avertissements ;
- les synthèses par sévérité, code et colonne ;
- la table détaillée des violations ;
- la lisibilité générale du rapport.

---

## 9. Tester explicitement un résultat valide

Exécuter ce test depuis PowerShell :

```powershell
@'
from pathlib import Path
import pandas as pd

from dataguardian import (
    generate_contract,
    generate_validation_html_report,
    profile_dataframe,
    save_validation_json,
    validate_dataframe,
    validation_exit_code,
)

df = pd.DataFrame({
    "customer_id": [1, 2, 3],
    "name": ["Alice", "Bob", "Charlie"],
})

contract = generate_contract(profile_dataframe(df))
result = validate_dataframe(df, contract)

save_validation_json(
    result,
    Path("artifacts/validation_valid.json"),
)

generate_validation_html_report(
    result,
    Path("artifacts/validation_valid_report.html"),
)

print("is_valid:", result.is_valid)
print("violation_count:", result.violation_count)
print("exit_code:", validation_exit_code(result))
'@ | python
```

Résultat attendu :

```text
is_valid: True
violation_count: 0
exit_code: 0
```

Ouvrir le rapport :

```powershell
Start-Process .\artifacts\validation_valid_report.html
```

Il doit afficher :

- `VALID` ;
- `0` violation ;
- `No contract violation detected.`

---

## 10. Tester les codes de sortie

### Cas conforme

Résultat attendu :

```text
0
```

### Cas non conforme

```powershell
python examples/validation_report_demo.py
$LASTEXITCODE
```

Résultat attendu si le dataset est non conforme :

```text
1
```

### Cas d'erreur technique

Renommer temporairement le contrat :

```powershell
Rename-Item `
    .\artifacts\contract.yaml `
    .\artifacts\contract.backup.yaml

python examples/validation_report_demo.py
$LASTEXITCODE
```

Résultat attendu :

```text
2
```

Restaurer ensuite le contrat :

```powershell
Rename-Item `
    .\artifacts\contract.backup.yaml `
    .\artifacts\contract.yaml
```

---

## 11. Tester la protection HTML

```powershell
python -m pytest tests/test_validation_report.py::test_html_report_escapes_dynamic_content -v
```

Résultat attendu :

```text
1 passed
```

Ce test vérifie qu'un contenu tel que :

```html
<script>alert(1)</script>
```

est écrit sous forme échappée :

```html
&lt;script&gt;alert(1)&lt;/script&gt;
```

---

## 12. Vérifier l'API publique

```powershell
python -c "import dataguardian; print(dataguardian.__all__)"
```

La liste doit notamment contenir :

```text
validation_result_to_dict
save_validation_json
generate_validation_html_report
validation_exit_code
```

---

## 13. Vérifier Git et GitHub Actions

Avant le commit :

```powershell
git status
git diff
```

Si tous les tests passent :

```powershell
git add .
git commit -m "Add validation JSON and HTML reporting"
git push origin main
```

Sur GitHub, vérifier que le workflow :

- installe correctement DataGuardian ;
- découvre le nouveau fichier de tests ;
- exécute toute la suite ;
- termine au vert.

Le script `examples/validation_report_demo.py` ne doit pas être traité comme un test classique sans gestion explicite de son code de sortie, car il retourne volontairement `1` lorsque le dataset est non conforme.

---

## Commandes essentielles

```powershell
python -m pip install -e ".[dev]"
python -m pytest -v
python examples/contract_demo.py
python examples/validation_report_demo.py
$LASTEXITCODE
```

---

## Checklist finale

```text
[ ] Python 3.12 actif
[ ] Package installé en mode editable
[ ] Version 0.6.0 confirmée
[ ] Nouvelles fonctions importables
[ ] Tests de la v0.6 au vert
[ ] Suite complète au vert
[ ] contract.yaml généré
[ ] validation.json généré
[ ] validation_report.html généré
[ ] JSON cohérent avec la liste des violations
[ ] Rapport HTML lisible
[ ] Cas VALID testé
[ ] Cas INVALID testé
[ ] Code technique 2 testé
[ ] Protection HTML testée
[ ] Commit et push effectués
[ ] GitHub Actions au vert
```
