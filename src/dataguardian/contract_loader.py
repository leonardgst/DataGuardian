from pathlib import Path
from typing import Any

import yaml

from dataguardian.contracts import (
    ColumnContract,
    DatasetContract,
)


SUPPORTED_CONTRACT_VERSIONS = {"1.0"}


def load_contract_yaml(
    filepath: str | Path,
) -> DatasetContract:
    """
    Charge un contrat YAML et le convertit en DatasetContract.

    Une erreur explicite est levée si le fichier est absent,
    vide, mal structuré ou utilise une version non prise en charge.
    """

    input_path = Path(filepath)

    if not input_path.exists():
        raise FileNotFoundError(
            f"Contract file not found: {input_path}"
        )

    if not input_path.is_file():
        raise ValueError(
            f"Contract path is not a file: {input_path}"
        )

    with input_path.open(
        mode="r",
        encoding="utf-8",
    ) as file:
        content = yaml.safe_load(file)

    if not isinstance(content, dict):
        raise ValueError(
            "Contract YAML must contain a mapping at its root."
        )

    _validate_required_fields(content)

    contract_version = str(content["contract_version"])

    if contract_version not in SUPPORTED_CONTRACT_VERSIONS:
        raise ValueError(
            f"Unsupported contract version: {contract_version}"
        )

    raw_columns = content["columns"]

    if not isinstance(raw_columns, list):
        raise ValueError(
            "Contract field 'columns' must contain a list."
        )

    columns = [
        _build_column_contract(raw_column)
        for raw_column in raw_columns
    ]

    try:
        column_count = int(content["column_count"])
        max_duplicate_rate = float(
            content["max_duplicate_rate"]
        )
        min_completeness_score = float(
            content["min_completeness_score"]
        )
        allow_extra_columns = _parse_boolean(
            content["allow_extra_columns"],
            field_name="allow_extra_columns",
        )
    except (TypeError, ValueError) as error:
        raise ValueError(
            "Contract contains invalid dataset constraints."
        ) from error

    _validate_rate(
        max_duplicate_rate,
        field_name="max_duplicate_rate",
    )
    _validate_rate(
        min_completeness_score,
        field_name="min_completeness_score",
    )

    if column_count < 0:
        raise ValueError(
            "Contract field 'column_count' must be "
            "greater than or equal to 0."
        )

    if column_count != len(columns):
        raise ValueError(
            "Contract field 'column_count' does not match "
            "the number of declared columns."
        )

    column_names = [
        column.name
        for column in columns
    ]

    if len(column_names) != len(set(column_names)):
        raise ValueError(
            "Contract contains duplicate column declarations."
        )

    return DatasetContract(
        contract_version=contract_version,
        column_count=column_count,
        allow_extra_columns=allow_extra_columns,
        max_duplicate_rate=max_duplicate_rate,
        min_completeness_score=min_completeness_score,
        columns=columns,
    )


def _build_column_contract(
    content: Any,
) -> ColumnContract:
    """
    Construit un contrat de colonne depuis un dictionnaire.
    """

    if not isinstance(content, dict):
        raise ValueError(
            "Each contract column must be a mapping."
        )

    required_fields = {
        "name",
        "dtype",
        "required",
        "min_completeness",
        "unique",
    }

    missing_fields = required_fields - content.keys()

    if missing_fields:
        missing = ", ".join(sorted(missing_fields))

        raise ValueError(
            f"Contract column is missing fields: {missing}"
        )

    name = content["name"]
    dtype = content["dtype"]

    if not isinstance(name, str) or not name.strip():
        raise ValueError(
            "Contract column field 'name' must be "
            "a non-empty string."
        )

    if not isinstance(dtype, str) or not dtype.strip():
        raise ValueError(
            "Contract column field 'dtype' must be "
            "a non-empty string."
        )

    try:
        min_completeness = float(
            content["min_completeness"]
        )
        required = _parse_boolean(
            content["required"],
            field_name="required",
        )
        unique = _parse_boolean(
            content["unique"],
            field_name="unique",
        )
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"Contract contains invalid constraints "
            f"for column '{name}'."
        ) from error

    _validate_rate(
        min_completeness,
        field_name=(
            f"columns.{name}.min_completeness"
        ),
    )

    return ColumnContract(
        name=name,
        dtype=dtype,
        required=required,
        min_completeness=min_completeness,
        unique=unique,
    )


def _validate_required_fields(
    content: dict[str, Any],
) -> None:
    """
    Vérifie la présence des champs principaux du contrat.
    """

    required_fields = {
        "contract_version",
        "column_count",
        "allow_extra_columns",
        "max_duplicate_rate",
        "min_completeness_score",
        "columns",
    }

    missing_fields = required_fields - content.keys()

    if missing_fields:
        missing = ", ".join(sorted(missing_fields))

        raise ValueError(
            f"Contract is missing required fields: {missing}"
        )


def _parse_boolean(
    value: Any,
    *,
    field_name: str,
) -> bool:
    """
    Vérifie qu'une valeur YAML est un booléen réel.

    Cela évite qu'une chaîne comme "false" soit interprétée
    comme vraie avec bool("false").
    """

    if not isinstance(value, bool):
        raise ValueError(
            f"Contract field '{field_name}' must be a boolean."
        )

    return value


def _validate_rate(
    value: float,
    *,
    field_name: str,
) -> None:
    """
    Vérifie qu'un taux est compris entre 0 et 1.
    """

    if not 0.0 <= value <= 1.0:
        raise ValueError(
            f"Contract field '{field_name}' must be "
            "between 0.0 and 1.0."
        )
