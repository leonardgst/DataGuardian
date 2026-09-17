# DataGuardian - Journal de développement n°4

## Objectif de l'itération

Introduire un premier système de **contrats de données réutilisables** afin de transformer les métriques observées par DataGuardian en attentes formalisées et exportables.

Cette itération couvre uniquement la **génération d'un contrat YAML à partir d'un `DatasetProfile`**. Le chargement d'un contrat et la validation d'un nouveau DataFrame seront traités dans une itération ultérieure.

## Positionnement fonctionnel

Le flux cible de cette version est le suivant :

```text
DataFrame
    ↓
DatasetProfile
    ↓
DatasetContract
    ↓
contract.yaml
```

Le projet distingue désormais clairement :

- le **profil**, qui décrit ce qui a été observé ;
- le **contrat**, qui décrit ce qui sera attendu lors de futures validations.

## Nouveaux fichiers

### `src/dataguardian/contracts.py`

Ce module définit les objets métier utilisés pour représenter un contrat de données.

```python
from dataclasses import dataclass


@dataclass(slots=True)
class ColumnContract:
    """Contraintes attendues pour une colonne."""

    name: str
    dtype: str
    required: bool
    min_completeness: float
    unique: bool


@dataclass(slots=True)
class DatasetContract:
    """Contrat décrivant la structure attendue d'un dataset."""

    contract_version: str
    column_count: int
    allow_extra_columns: bool
    max_duplicate_rate: float
    min_completeness_score: float
    columns: list[ColumnContract]
```

### `src/dataguardian/contract_generator.py`

Ce module génère un contrat depuis un profil et permet son export au format YAML.

```python
from dataclasses import asdict
from pathlib import Path

import yaml

from dataguardian.contracts import ColumnContract, DatasetContract
from dataguardian.models import DatasetProfile


def generate_contract(
    profile: DatasetProfile,
    *,
    completeness_tolerance: float = 0.05,
    duplicate_rate_tolerance: float = 0.05,
    allow_extra_columns: bool = False,
) -> DatasetContract:
    """
    Génère un contrat de données à partir d'un profil existant.

    La tolérance de complétude permet d'éviter de construire un contrat
    excessivement strict à partir d'un seul dataset.
    """

    _validate_tolerance(
        completeness_tolerance,
        parameter_name="completeness_tolerance",
    )
    _validate_tolerance(
        duplicate_rate_tolerance,
        parameter_name="duplicate_rate_tolerance",
    )

    column_contracts: list[ColumnContract] = []

    for column in profile.columns:
        min_completeness = max(
            0.0,
            column.completeness - completeness_tolerance,
        )

        column_contracts.append(
            ColumnContract(
                name=column.name,
                dtype=column.dtype,
                required=True,
                min_completeness=round(min_completeness, 4),
                unique=(
                    column.non_null_count > 0
                    and column.uniqueness_ratio == 1.0
                ),
            )
        )

    min_completeness_score = max(
        0.0,
        profile.completeness_score - completeness_tolerance,
    )

    max_duplicate_rate = min(
        1.0,
        profile.duplicate_rate + duplicate_rate_tolerance,
    )

    return DatasetContract(
        contract_version="1.0",
        column_count=profile.column_count,
        allow_extra_columns=allow_extra_columns,
        max_duplicate_rate=round(max_duplicate_rate, 4),
        min_completeness_score=round(min_completeness_score, 4),
        columns=column_contracts,
    )


def save_contract_yaml(
    contract: DatasetContract,
    filepath: str | Path,
) -> None:
    """Enregistre un contrat de données au format YAML."""

    output_path = Path(filepath)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open(mode="w", encoding="utf-8") as file:
        yaml.safe_dump(
            asdict(contract),
            file,
            sort_keys=False,
            allow_unicode=True,
        )


def generate_contract_yaml(
    profile: DatasetProfile,
    filepath: str | Path,
    *,
    completeness_tolerance: float = 0.05,
    duplicate_rate_tolerance: float = 0.05,
    allow_extra_columns: bool = False,
) -> DatasetContract:
    """Génère un contrat depuis un profil et l'enregistre en YAML."""

    contract = generate_contract(
        profile,
        completeness_tolerance=completeness_tolerance,
        duplicate_rate_tolerance=duplicate_rate_tolerance,
        allow_extra_columns=allow_extra_columns,
    )

    save_contract_yaml(contract, filepath)
    return contract


def _validate_tolerance(
    value: float,
    *,
    parameter_name: str,
) -> None:
    """Vérifie qu'une tolérance est comprise entre 0 et 1."""

    if not 0.0 <= value <= 1.0:
        raise ValueError(
            f"{parameter_name} must be between 0.0 and 1.0"
        )
```

## Logique de génération

### Complétude

La complétude minimale est calculée en retranchant une tolérance à la valeur observée :

```text
min_completeness = completeness observée - tolérance
```

Exemple :

```text
Complétude observée : 0.95
Tolérance :           0.05
Minimum attendu :     0.90
```

Le résultat ne peut pas être inférieur à `0.0`.

### Doublons

Le taux maximal de doublons est calculé en ajoutant une tolérance au taux observé :

```text
max_duplicate_rate = duplicate_rate observé + tolérance
```

Le résultat ne peut pas dépasser `1.0`.

### Unicité

Une colonne est déclarée unique lorsque :

- elle contient au moins une valeur non nulle ;
- son taux d'unicité est égal à `1.0`.

### Colonnes supplémentaires

Par défaut, le contrat est strict :

```yaml
allow_extra_columns: false
```

Cette option peut être modifiée lors de la génération du contrat.

## Mise à jour de l'API publique

### Fichier `src/dataguardian/__init__.py`

Remplacer son contenu par :

```python
from dataguardian.api import profile_dataframe
from dataguardian.contract_generator import (
    generate_contract,
    generate_contract_yaml,
    save_contract_yaml,
)
from dataguardian.html_report import generate_html_report
from dataguardian.report import save_summary_json

__all__ = [
    "profile_dataframe",
    "save_summary_json",
    "generate_html_report",
    "generate_contract",
    "save_contract_yaml",
    "generate_contract_yaml",
]
```

## Mise à jour du projet

### Fichier `pyproject.toml`

La dépendance `PyYAML` doit être ajoutée et la version du projet passe à `0.4.0`.

```toml
[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[project]
name = "dataguardian"
version = "0.4.0"
description = "Data profiling and quality assessment library"
requires-python = ">=3.11"

dependencies = [
    "pandas>=2.0",
    "PyYAML>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]
```

## Tests à ajouter

### `tests/test_contract_generator.py`

```python
from pathlib import Path

import pandas as pd
import pytest
import yaml

from dataguardian import (
    generate_contract,
    generate_contract_yaml,
    profile_dataframe,
)


def test_generate_contract_contains_dataset_constraints():
    df = pd.DataFrame(
        {
            "customer_id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
        }
    )

    profile = profile_dataframe(df)
    contract = generate_contract(profile)

    assert contract.contract_version == "1.0"
    assert contract.column_count == 2
    assert contract.allow_extra_columns is False
    assert contract.max_duplicate_rate == 0.05
    assert contract.min_completeness_score == 0.95


def test_generate_contract_contains_column_constraints():
    df = pd.DataFrame(
        {
            "customer_id": [1, 2, 3],
            "city": ["Paris", "Paris", None],
        }
    )

    profile = profile_dataframe(df)
    contract = generate_contract(
        profile,
        completeness_tolerance=0.05,
    )

    customer_id_contract = contract.columns[0]
    city_contract = contract.columns[1]

    assert customer_id_contract.name == "customer_id"
    assert customer_id_contract.dtype == "int64"
    assert customer_id_contract.required is True
    assert customer_id_contract.min_completeness == 0.95
    assert customer_id_contract.unique is True

    assert city_contract.name == "city"
    assert city_contract.min_completeness == 0.6167
    assert city_contract.unique is False


def test_generate_contract_yaml_creates_file(tmp_path: Path):
    df = pd.DataFrame(
        {
            "customer_id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
        }
    )

    profile = profile_dataframe(df)
    output_path = tmp_path / "contract.yaml"

    generate_contract_yaml(profile, output_path)

    assert output_path.exists()


def test_generated_yaml_contains_expected_content(tmp_path: Path):
    df = pd.DataFrame(
        {
            "customer_id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
        }
    )

    profile = profile_dataframe(df)
    output_path = tmp_path / "contract.yaml"

    generate_contract_yaml(profile, output_path)

    with output_path.open(mode="r", encoding="utf-8") as file:
        content = yaml.safe_load(file)

    assert content["contract_version"] == "1.0"
    assert content["column_count"] == 2
    assert content["allow_extra_columns"] is False
    assert len(content["columns"]) == 2
    assert content["columns"][0]["name"] == "customer_id"
    assert content["columns"][0]["unique"] is True


def test_generate_contract_rejects_invalid_tolerance():
    df = pd.DataFrame({"customer_id": [1, 2, 3]})
    profile = profile_dataframe(df)

    with pytest.raises(ValueError, match="completeness_tolerance"):
        generate_contract(
            profile,
            completeness_tolerance=1.5,
        )
```

## Script de démonstration

### `examples/contract_demo.py`

```python
from pathlib import Path

import pandas as pd

from dataguardian import (
    generate_contract_yaml,
    profile_dataframe,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "examples" / "dirty_customers.csv"
OUTPUT_FILE = PROJECT_ROOT / "artifacts" / "contract.yaml"


def main() -> None:
    df = pd.read_csv(INPUT_FILE)
    profile = profile_dataframe(df)

    contract = generate_contract_yaml(
        profile,
        OUTPUT_FILE,
        completeness_tolerance=0.05,
        duplicate_rate_tolerance=0.05,
        allow_extra_columns=False,
    )

    print(f"Contract generated: {OUTPUT_FILE}")
    print(f"Contract version: {contract.contract_version}")
    print(f"Expected columns: {contract.column_count}")


if __name__ == "__main__":
    main()
```

## Artefact produit

Après exécution du script de démonstration, le fichier suivant est créé :

```text
artifacts/contract.yaml
```

Exemple de résultat :

```yaml
contract_version: '1.0'
column_count: 2
allow_extra_columns: false
max_duplicate_rate: 0.05
min_completeness_score: 0.95
columns:
- name: customer_id
  dtype: int64
  required: true
  min_completeness: 0.95
  unique: true
- name: name
  dtype: object
  required: true
  min_completeness: 0.95
  unique: true
```

## Arborescence cible

```text
dataguardian
+----artifacts
|    contract.yaml
|    report.html
|    summary.json
|
+----examples
|    contract_demo.py
|    customers.csv
|    dirty_customers.csv
|    report_demo.py
|
+----src
|    +----dataguardian
|         __init__.py
|         api.py
|         contract_generator.py
|         contracts.py
|         html_report.py
|         models.py
|         profiler.py
|         quality.py
|         report.py
|
+----tests
     test_contract_generator.py
     test_html_report.py
     test_profiler.py
     test_quality.py
     test_report.py
```

## Commandes d'installation et de validation

Depuis la racine du projet :

### Réinstaller le package

```powershell
pip install -e ".[dev]"
```

### Exécuter tous les tests

```powershell
pytest -v
```

### Exécuter uniquement les nouveaux tests

```powershell
pytest tests/test_contract_generator.py -v
```

### Générer le contrat YAML

```powershell
python examples/contract_demo.py
```

## Commandes Git

Lorsque l'ensemble des tests est au vert :

```powershell
git status
git add .
git commit -m "Add YAML data contract generation"
git push origin main
```

## État attendu à la fin de l'itération

- Modèles de contrat dataset et colonne créés.
- Génération d'un contrat depuis un `DatasetProfile`.
- Paramètres de tolérance contrôlés.
- Export YAML fonctionnel.
- API publique mise à jour.
- Dépendance PyYAML ajoutée.
- Tests unitaires ajoutés et validés.
- Script de démonstration opérationnel.
- Fichier `artifacts/contract.yaml` généré.

## Prochaine étape envisagée

La prochaine itération pourra introduire le moteur de validation :

```text
Nouveau DataFrame + contract.yaml
                ↓
        Chargement du contrat
                ↓
        Validation des données
                ↓
      Liste structurée des violations
```

Les contrôles candidats sont :

- présence des colonnes obligatoires ;
- détection des colonnes supplémentaires ;
- conformité des types ;
- respect de la complétude minimale ;
- respect des contraintes d'unicité ;
- respect du taux maximal de doublons ;
- respect du score global de complétude.
