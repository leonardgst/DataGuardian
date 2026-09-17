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

    Exemple :
        complétude observée = 0.95
        tolérance = 0.05
        complétude minimale attendue = 0.90
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
    """
    Enregistre un contrat de données au format YAML.

    Le dossier parent est créé automatiquement s'il n'existe pas.
    """

    output_path = Path(filepath)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    contract_data = asdict(contract)

    with output_path.open(
        mode="w",
        encoding="utf-8",
    ) as file:
        yaml.safe_dump(
            contract_data,
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
    """
    Génère un contrat depuis un profil et l'enregistre au format YAML.

    Retourne également le contrat créé afin qu'il puisse être utilisé
    directement par le code appelant.
    """

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