import pandas as pd

from dataguardian.contracts import (
    ContractViolation,
    DatasetContract,
    ValidationResult,
)
from dataguardian.profiler import profile_dataframe


def validate_dataframe(
    df: pd.DataFrame,
    contract: DatasetContract,
) -> ValidationResult:
    """
    Valide un DataFrame par rapport à un contrat.

    Tous les contrôles sont exécutés afin de retourner
    l'ensemble des violations détectées.
    """

    violations: list[ContractViolation] = []

    expected_columns = {
        column.name
        for column in contract.columns
    }

    observed_columns = {
        str(column)
        for column in df.columns
    }

    _validate_missing_columns(
        observed_columns=observed_columns,
        contract=contract,
        violations=violations,
    )

    _validate_extra_columns(
        expected_columns=expected_columns,
        observed_columns=observed_columns,
        contract=contract,
        violations=violations,
    )

    _validate_column_constraints(
        df=df,
        contract=contract,
        violations=violations,
    )

    profile = profile_dataframe(df)

    _validate_dataset_constraints(
        duplicate_rate=profile.duplicate_rate,
        completeness_score=profile.completeness_score,
        contract=contract,
        violations=violations,
    )

    return ValidationResult(
        violations=violations,
    )


def _validate_missing_columns(
    *,
    observed_columns: set[str],
    contract: DatasetContract,
    violations: list[ContractViolation],
) -> None:
    """
    Détecte les colonnes obligatoires absentes.
    """

    for column_contract in contract.columns:
        if (
            column_contract.required
            and column_contract.name not in observed_columns
        ):
            violations.append(
                ContractViolation(
                    code="MISSING_COLUMN",
                    severity="ERROR",
                    column=column_contract.name,
                    expected="column present",
                    observed="column missing",
                    message=(
                        f"Required column "
                        f"'{column_contract.name}' is missing."
                    ),
                )
            )


def _validate_extra_columns(
    *,
    expected_columns: set[str],
    observed_columns: set[str],
    contract: DatasetContract,
    violations: list[ContractViolation],
) -> None:
    """
    Détecte les colonnes non déclarées dans le contrat.
    """

    if contract.allow_extra_columns:
        return

    extra_columns = sorted(
        observed_columns - expected_columns
    )

    for column_name in extra_columns:
        violations.append(
            ContractViolation(
                code="EXTRA_COLUMN",
                severity="ERROR",
                column=column_name,
                expected="column absent",
                observed="column present",
                message=(
                    f"Column '{column_name}' is not declared "
                    f"in the contract."
                ),
            )
        )


def _validate_column_constraints(
    *,
    df: pd.DataFrame,
    contract: DatasetContract,
    violations: list[ContractViolation],
) -> None:
    """
    Valide les contraintes définies au niveau des colonnes.
    """

    row_count = len(df)

    for column_contract in contract.columns:
        column_name = column_contract.name

        if column_name not in df.columns:
            continue

        series = df[column_name]

        _validate_column_dtype(
            series=series,
            column_name=column_name,
            expected_dtype=column_contract.dtype,
            violations=violations,
        )

        _validate_column_completeness(
            series=series,
            column_name=column_name,
            row_count=row_count,
            min_completeness=(
                column_contract.min_completeness
            ),
            violations=violations,
        )

        if column_contract.unique:
            _validate_column_uniqueness(
                series=series,
                column_name=column_name,
                violations=violations,
            )


def _validate_column_dtype(
    *,
    series: pd.Series,
    column_name: str,
    expected_dtype: str,
    violations: list[ContractViolation],
) -> None:
    """
    Vérifie le type Pandas d'une colonne.
    """

    observed_dtype = str(series.dtype)

    if observed_dtype == expected_dtype:
        return

    violations.append(
        ContractViolation(
            code="INVALID_DTYPE",
            severity="ERROR",
            column=column_name,
            expected=expected_dtype,
            observed=observed_dtype,
            message=(
                f"Column '{column_name}' has dtype "
                f"'{observed_dtype}' instead of "
                f"'{expected_dtype}'."
            ),
        )
    )


def _validate_column_completeness(
    *,
    series: pd.Series,
    column_name: str,
    row_count: int,
    min_completeness: float,
    violations: list[ContractViolation],
) -> None:
    """
    Vérifie la complétude minimale d'une colonne.
    """

    non_null_count = int(series.notna().sum())

    completeness = (
        non_null_count / row_count
        if row_count > 0
        else 0.0
    )

    completeness = round(completeness, 4)

    if completeness >= min_completeness:
        return

    violations.append(
        ContractViolation(
            code="MIN_COMPLETENESS",
            severity="ERROR",
            column=column_name,
            expected=min_completeness,
            observed=completeness,
            message=(
                f"Column '{column_name}' has completeness "
                f"{completeness}, below the required minimum "
                f"{min_completeness}."
            ),
        )
    )


def _validate_column_uniqueness(
    *,
    series: pd.Series,
    column_name: str,
    violations: list[ContractViolation],
) -> None:
    """
    Vérifie l'unicité des valeurs non nulles d'une colonne.

    Les valeurs nulles sont ignorées car elles sont déjà
    contrôlées par la règle de complétude.
    """

    duplicate_values = int(
        series.dropna().duplicated().sum()
    )

    if duplicate_values == 0:
        return

    violations.append(
        ContractViolation(
            code="UNIQUENESS",
            severity="ERROR",
            column=column_name,
            expected="unique values",
            observed=(
                f"{duplicate_values} duplicate values"
            ),
            message=(
                f"Column '{column_name}' contains "
                f"{duplicate_values} duplicate values."
            ),
        )
    )


def _validate_dataset_constraints(
    *,
    duplicate_rate: float,
    completeness_score: float,
    contract: DatasetContract,
    violations: list[ContractViolation],
) -> None:
    """
    Valide les contraintes définies au niveau du dataset.
    """

    if duplicate_rate > contract.max_duplicate_rate:
        violations.append(
            ContractViolation(
                code="MAX_DUPLICATE_RATE",
                severity="ERROR",
                column=None,
                expected=contract.max_duplicate_rate,
                observed=duplicate_rate,
                message=(
                    f"Dataset duplicate rate is "
                    f"{duplicate_rate}, above the allowed "
                    f"maximum "
                    f"{contract.max_duplicate_rate}."
                ),
            )
        )

    if completeness_score < contract.min_completeness_score:
        violations.append(
            ContractViolation(
                code="MIN_COMPLETENESS_SCORE",
                severity="ERROR",
                column=None,
                expected=contract.min_completeness_score,
                observed=completeness_score,
                message=(
                    f"Dataset completeness score is "
                    f"{completeness_score}, below the required "
                    f"minimum "
                    f"{contract.min_completeness_score}."
                ),
            )
        )