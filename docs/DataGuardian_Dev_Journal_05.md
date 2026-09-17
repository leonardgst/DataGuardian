# DataGuardian - Journal de développement n°5

## Objectif de l'itération

Transformer les contrats YAML générés par DataGuardian en un véritable mécanisme de validation des nouvelles livraisons de données.

Cette version introduit :

- le chargement sécurisé d'un contrat YAML ;
- la conversion du contenu YAML en objets métier ;
- la validation d'un DataFrame par rapport au contrat ;
- la production d'un résultat structuré ;
- la détection détaillée des violations ;
- une suite complète de tests unitaires ;
- un script de démonstration.

## Évolution du flux fonctionnel

Le flux DataGuardian devient :

```text
Dataset de référence
        ↓
   profile_dataframe()
        ↓
   DatasetProfile
        ↓
   generate_contract()
        ↓
    contract.yaml
        ↓
 load_contract_yaml()
        ↓
   DatasetContract
        ↓
Nouvelle livraison
        ↓
 validate_dataframe()
        ↓
  ValidationResult
        ↓
Liste des violations
```

DataGuardian couvre maintenant les étapes suivantes :

- observer les données ;
- diagnostiquer leur qualité ;
- produire des rapports ;
- contractualiser les attentes ;
- valider de nouvelles livraisons.

## Évolution des modèles de contrat

### `ContractViolation`

Ajout d'une dataclass représentant une violation détectée pendant la validation.

Informations conservées :

- code de la violation ;
- niveau de sévérité ;
- colonne concernée ;
- valeur attendue ;
- valeur observée ;
- message explicatif.

### `ValidationResult`

Ajout d'une dataclass regroupant toutes les violations détectées.

Propriétés exposées :

- `is_valid`, qui indique si le contrat est entièrement respecté ;
- `violation_count`, qui retourne le nombre total de violations ;
- `violations`, qui contient le détail des anomalies.

## Chargement des contrats YAML

### Nouveau module

```text
src/dataguardian/contract_loader.py
```

### Fonction publique

```python
load_contract_yaml(filepath)
```

Cette fonction :

1. vérifie que le fichier existe et correspond à un fichier régulier ;
2. charge le YAML avec `yaml.safe_load()` ;
3. vérifie la présence des champs obligatoires ;
4. contrôle la version du contrat ;
5. valide les types et les taux configurés ;
6. vérifie la cohérence entre `column_count` et les colonnes déclarées ;
7. refuse les déclarations de colonnes dupliquées ;
8. construit un objet `DatasetContract`.

### Version de contrat prise en charge

```text
1.0
```

### Contrôles de structure

Le chargeur rejette notamment :

- un fichier absent ;
- un fichier vide ;
- une racine YAML qui n'est pas un dictionnaire ;
- un contrat incomplet ;
- une version non prise en charge ;
- un booléen écrit comme une chaîne de caractères ;
- un taux inférieur à 0 ou supérieur à 1 ;
- un nombre de colonnes incohérent ;
- une colonne déclarée plusieurs fois.

## Moteur de validation

### Nouveau module

```text
src/dataguardian/validator.py
```

### Fonction publique

```python
validate_dataframe(df, contract)
```

Le moteur exécute l'ensemble des contrôles avant de retourner un `ValidationResult`. Il ne s'arrête donc pas à la première erreur.

## Violations prises en charge

### `MISSING_COLUMN`

Détecte une colonne obligatoire absente de la nouvelle livraison.

### `EXTRA_COLUMN`

Détecte une colonne non déclarée lorsque le contrat contient :

```yaml
allow_extra_columns: false
```

### `INVALID_DTYPE`

Compare le type Pandas observé avec le type attendu dans le contrat.

La comparaison est stricte :

```text
int64 != float64
int64 != str
```

### `MIN_COMPLETENESS`

Vérifie que la complétude de chaque colonne est supérieure ou égale au seuil attendu.

### `UNIQUENESS`

Vérifie l'unicité des valeurs non nulles des colonnes concernées.

Les valeurs nulles sont volontairement exclues de ce contrôle, car elles sont déjà couvertes par la contrainte de complétude.

### `MAX_DUPLICATE_RATE`

Vérifie que le taux de lignes entièrement dupliquées ne dépasse pas le maximum autorisé.

### `MIN_COMPLETENESS_SCORE`

Vérifie que le score global de complétude du dataset respecte le minimum défini dans le contrat.

## API publique

Mise à jour de :

```text
src/dataguardian/__init__.py
```

Nouvelles fonctions exposées :

```python
load_contract_yaml
validate_dataframe
```

L'utilisation publique devient :

```python
from dataguardian import (
    load_contract_yaml,
    validate_dataframe,
)
```

## Script de démonstration

### Nouveau fichier

```text
examples/validation_demo.py
```

Le script :

- charge `examples/dirty_customers.csv` ;
- charge `artifacts/contract.yaml` ;
- valide le DataFrame ;
- affiche le statut global ;
- affiche le nombre de violations ;
- détaille chaque violation dans le terminal.

Le contrat doit d'abord être généré avec :

```powershell
python examples/contract_demo.py
```

La validation peut ensuite être lancée avec :

```powershell
python examples/validation_demo.py
```

## Tests ajoutés

### Nouveau fichier

```text
tests/test_contract_validation.py
```

Les tests couvrent :

- un DataFrame entièrement valide ;
- une colonne obligatoire manquante ;
- une colonne supplémentaire interdite ;
- une colonne supplémentaire autorisée ;
- un type de données incorrect ;
- une complétude de colonne insuffisante ;
- une complétude globale insuffisante ;
- une violation d'unicité ;
- l'exclusion des valeurs nulles du contrôle d'unicité ;
- un taux de doublons trop élevé ;
- la génération et le chargement d'un contrat YAML ;
- la validation avec un contrat rechargé ;
- un fichier de contrat absent ;
- un contrat vide ;
- une structure incomplète ;
- une version non prise en charge ;
- un booléen YAML invalide ;
- un taux hors limites ;
- une incohérence du nombre de colonnes.

## Problème rencontré

### Différence de type texte selon la version de Pandas

Le test du type incorrect attendait initialement :

```text
object
```

Sur l'environnement utilisé avec Python 3.12 et la version installée de Pandas, le type observé est :

```text
str
```

Le moteur de validation fonctionnait correctement. Seule l'assertion du test était trop dépendante d'une version précise de Pandas.

### Correction

L'assertion fixe :

```python
assert dtype_violations[0].observed == "object"
```

est remplacée par une comparaison avec le type réellement inféré :

```python
assert dtype_violations[0].observed == str(
    delivery_df["customer_id"].dtype
)
```

Une assertion complémentaire vérifie que le type observé reste différent du type attendu :

```python
assert (
    dtype_violations[0].observed
    != dtype_violations[0].expected
)
```

Cette correction rend le test compatible avec les différentes représentations des colonnes texte dans Pandas.

## Validation de l'itération

Résultat avant la correction du test :

```text
33 passed, 1 failed
```

L'unique échec concernait l'attente `object` contre le type réellement observé `str`.

Résultat attendu après correction :

```text
34 passed
```

## Version du projet

Le fichier `pyproject.toml` passe à :

```toml
version = "0.5.0"
```

Les dépendances restent :

```toml
dependencies = [
    "pandas>=2.0",
    "PyYAML>=6.0",
]
```

## Arborescence fonctionnelle obtenue

```text
dataguardian
+----artifacts
|    contract.yaml
|    report.html
|    summary.json
|
+----docs
|    DataGuardian_Dev_Journal_01.md
|    DataGuardian_Dev_Journal_02.md
|    DataGuardian_Dev_Journal_03.md
|    DataGuardian_Dev_Journal_04.md
|    DataGuardian_Dev_Journal_05.md
|
+----examples
|    contract_demo.py
|    customers.csv
|    dirty_customers.csv
|    report_demo.py
|    validation_demo.py
|
+----src
|    +----dataguardian
|         __init__.py
|         api.py
|         contract_generator.py
|         contract_loader.py
|         contracts.py
|         html_report.py
|         models.py
|         profiler.py
|         quality.py
|         report.py
|         validator.py
|
+----tests
     test_contract_generator.py
     test_contract_validation.py
     test_html_report.py
     test_profiler.py
     test_quality.py
     test_report.py
```

## Commandes de validation

### Exécuter tous les tests

```powershell
python -m pytest -v
```

### Tester le flux complet

```powershell
python examples/contract_demo.py
python examples/validation_demo.py
```

## État du projet à la fin de la v0.5

- Package Python installable.
- CI GitHub Actions existante.
- Profilage structurel opérationnel.
- Métriques et alertes qualité disponibles.
- Export JSON disponible.
- Rapport HTML disponible.
- Génération de contrats YAML disponible.
- Chargement sécurisé des contrats YAML disponible.
- Validation des nouvelles livraisons disponible.
- Violations structurées et exploitables.
- Suite de tests étendue.

## Prochaine étape envisagée : v0.6

La prochaine version pourra rendre les résultats de validation exploitables par les utilisateurs et les systèmes automatisés.

Fonctionnalités candidates :

- export de `ValidationResult` dans `validation.json` ;
- génération d'un rapport `validation_report.html` ;
- synthèse des contrôles réussis et échoués ;
- regroupement des violations par sévérité et par colonne ;
- métadonnées d'exécution ;
- préparation d'un code de sortie exploitable dans une CI.

Flux cible :

```text
ValidationResult
       ↓
+-------------------------+
|                         |
validation.json    validation_report.html
|                         |
Automatisation       Consultation humaine
```
