from pathlib import Path

import pandas as pd
import pytest

from dataguardian import (
    generate_contract,
    generate_contract_yaml,
    load_contract_yaml,
    profile_dataframe,
    validate_dataframe,
)


def test_valid_dataframe_passes_contract():
    reference_df = pd.DataFrame(
        {
            "customer_id": [1, 2, 3],
            "city": ["Paris", "Lyon", "Nantes"],
        }
    )

    contract = generate_contract(
        profile_dataframe(reference_df)
    )

    result = validate_dataframe(
        reference_df,
        contract,
    )

    assert result.is_valid is True
    assert result.violation_count == 0
    assert result.violations == []


def test_missing_required_column_is_detected():
    reference_df = pd.DataFrame(
        {
            "customer_id": [1, 2, 3],
            "city": ["Paris", "Lyon", "Nantes"],
        }
    )

    delivery_df = pd.DataFrame(
        {
            "customer_id": [4, 5, 6],
        }
    )

    contract = generate_contract(
        profile_dataframe(reference_df)
    )

    result = validate_dataframe(
        delivery_df,
        contract,
    )

    missing_column_violations = [
        violation
        for violation in result.violations
        if violation.code == "MISSING_COLUMN"
    ]

    assert result.is_valid is False
    assert len(missing_column_violations) == 1
    assert missing_column_violations[0].column == "city"


def test_extra_column_is_detected():
    reference_df = pd.DataFrame(
        {
            "customer_id": [1, 2, 3],
        }
    )

    delivery_df = pd.DataFrame(
        {
            "customer_id": [4, 5, 6],
            "unexpected_column": ["A", "B", "C"],
        }
    )

    contract = generate_contract(
        profile_dataframe(reference_df),
        allow_extra_columns=False,
    )

    result = validate_dataframe(
        delivery_df,
        contract,
    )

    extra_column_violations = [
        violation
        for violation in result.violations
        if violation.code == "EXTRA_COLUMN"
    ]

    assert len(extra_column_violations) == 1
    assert (
        extra_column_violations[0].column
        == "unexpected_column"
    )


def test_extra_column_is_allowed_when_configured():
    reference_df = pd.DataFrame(
        {
            "customer_id": [1, 2, 3],
        }
    )

    delivery_df = pd.DataFrame(
        {
            "customer_id": [4, 5, 6],
            "new_column": ["A", "B", "C"],
        }
    )

    contract = generate_contract(
        profile_dataframe(reference_df),
        allow_extra_columns=True,
    )

    result = validate_dataframe(
        delivery_df,
        contract,
    )

    violation_codes = {
        violation.code
        for violation in result.violations
    }

    assert "EXTRA_COLUMN" not in violation_codes


def test_invalid_dtype_is_detected():
    reference_df = pd.DataFrame(
        {
            "customer_id": [1, 2, 3],
        }
    )

    delivery_df = pd.DataFrame(
        {
            "customer_id": ["1", "2", "3"],
        }
    )

    contract = generate_contract(
        profile_dataframe(reference_df)
    )

    result = validate_dataframe(
        delivery_df,
        contract,
    )

    dtype_violations = [
        violation
        for violation in result.violations
        if violation.code == "INVALID_DTYPE"
    ]

    assert len(dtype_violations) == 1
    assert dtype_violations[0].column == "customer_id"
    assert dtype_violations[0].expected == "int64"
    assert dtype_violations[0].observed == str(delivery_df["customer_id"].dtype)


def test_minimum_completeness_is_validated():
    reference_df = pd.DataFrame(
        {
            "customer_id": [1, 2, 3, 4],
            "city": [
                "Paris",
                "Lyon",
                "Nantes",
                "Lille",
            ],
        }
    )

    delivery_df = pd.DataFrame(
        {
            "customer_id": [5, 6, 7, 8],
            "city": [
                "Paris",
                None,
                None,
                None,
            ],
        }
    )

    contract = generate_contract(
        profile_dataframe(reference_df),
        completeness_tolerance=0.05,
    )

    result = validate_dataframe(
        delivery_df,
        contract,
    )

    completeness_violations = [
        violation
        for violation in result.violations
        if violation.code == "MIN_COMPLETENESS"
    ]

    assert len(completeness_violations) == 1
    assert completeness_violations[0].column == "city"
    assert completeness_violations[0].expected == 0.95
    assert completeness_violations[0].observed == 0.25


def test_global_completeness_is_validated():
    reference_df = pd.DataFrame(
        {
            "customer_id": [1, 2, 3, 4],
            "city": [
                "Paris",
                "Lyon",
                "Nantes",
                "Lille",
            ],
        }
    )

    delivery_df = pd.DataFrame(
        {
            "customer_id": [5, 6, 7, 8],
            "city": [
                "Paris",
                None,
                None,
                None,
            ],
        }
    )

    contract = generate_contract(
        profile_dataframe(reference_df),
        completeness_tolerance=0.05,
    )

    result = validate_dataframe(
        delivery_df,
        contract,
    )

    violation_codes = {
        violation.code
        for violation in result.violations
    }

    assert "MIN_COMPLETENESS_SCORE" in violation_codes


def test_uniqueness_constraint_is_validated():
    reference_df = pd.DataFrame(
        {
            "customer_id": [1, 2, 3],
        }
    )

    delivery_df = pd.DataFrame(
        {
            "customer_id": [1, 1, 2],
        }
    )

    contract = generate_contract(
        profile_dataframe(reference_df)
    )

    result = validate_dataframe(
        delivery_df,
        contract,
    )

    uniqueness_violations = [
        violation
        for violation in result.violations
        if violation.code == "UNIQUENESS"
    ]

    assert len(uniqueness_violations) == 1
    assert uniqueness_violations[0].column == "customer_id"
    assert (
        uniqueness_violations[0].observed
        == "1 duplicate values"
    )


def test_null_values_are_ignored_for_uniqueness():
    reference_df = pd.DataFrame(
        {
            "customer_id": [1.0, 2.0, 3.0, None],
        }
    )

    delivery_df = pd.DataFrame(
        {
            "customer_id": [4.0, 5.0, None, None],
        }
    )

    contract = generate_contract(
        profile_dataframe(reference_df),
        completeness_tolerance=0.30,
    )

    result = validate_dataframe(
        delivery_df,
        contract,
    )

    uniqueness_violations = [
        violation
        for violation in result.violations
        if violation.code == "UNIQUENESS"
    ]

    assert uniqueness_violations == []


def test_duplicate_rate_is_validated():
    reference_df = pd.DataFrame(
        {
            "customer_id": [1, 2, 3, 4],
            "city": [
                "Paris",
                "Lyon",
                "Nantes",
                "Lille",
            ],
        }
    )

    delivery_df = pd.DataFrame(
        {
            "customer_id": [1, 1, 1, 2],
            "city": [
                "Paris",
                "Paris",
                "Paris",
                "Lyon",
            ],
        }
    )

    contract = generate_contract(
        profile_dataframe(reference_df),
        duplicate_rate_tolerance=0.05,
    )

    result = validate_dataframe(
        delivery_df,
        contract,
    )

    duplicate_rate_violations = [
        violation
        for violation in result.violations
        if violation.code == "MAX_DUPLICATE_RATE"
    ]

    assert len(duplicate_rate_violations) == 1
    assert duplicate_rate_violations[0].column is None


def test_contract_can_be_loaded_from_yaml(
    tmp_path: Path,
):
    reference_df = pd.DataFrame(
        {
            "customer_id": [1, 2, 3],
            "city": ["Paris", "Lyon", "Nantes"],
        }
    )

    output_path = tmp_path / "contract.yaml"

    generate_contract_yaml(
        profile_dataframe(reference_df),
        output_path,
    )

    loaded_contract = load_contract_yaml(output_path)

    assert loaded_contract.contract_version == "1.0"
    assert loaded_contract.column_count == 2
    assert loaded_contract.allow_extra_columns is False
    assert len(loaded_contract.columns) == 2
    assert (
        loaded_contract.columns[0].name
        == "customer_id"
    )


def test_loaded_contract_can_validate_dataframe(
    tmp_path: Path,
):
    reference_df = pd.DataFrame(
        {
            "customer_id": [1, 2, 3],
            "city": ["Paris", "Lyon", "Nantes"],
        }
    )

    delivery_df = pd.DataFrame(
        {
            "customer_id": [4, 5, 6],
            "city": ["Lille", "Nice", "Rouen"],
        }
    )

    output_path = tmp_path / "contract.yaml"

    generate_contract_yaml(
        profile_dataframe(reference_df),
        output_path,
    )

    loaded_contract = load_contract_yaml(output_path)

    result = validate_dataframe(
        delivery_df,
        loaded_contract,
    )

    assert result.is_valid is True
    assert result.violation_count == 0


def test_missing_contract_file_raises_error(
    tmp_path: Path,
):
    missing_path = tmp_path / "missing.yaml"

    with pytest.raises(FileNotFoundError):
        load_contract_yaml(missing_path)


def test_empty_contract_raises_error(
    tmp_path: Path,
):
    empty_path = tmp_path / "empty.yaml"

    empty_path.write_text(
        "",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="mapping at its root",
    ):
        load_contract_yaml(empty_path)


def test_invalid_contract_structure_raises_error(
    tmp_path: Path,
):
    invalid_path = tmp_path / "invalid.yaml"

    invalid_path.write_text(
        "contract_version: '1.0'\n",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="missing required fields",
    ):
        load_contract_yaml(invalid_path)


def test_unsupported_contract_version_raises_error(
    tmp_path: Path,
):
    unsupported_path = tmp_path / "unsupported.yaml"

    unsupported_path.write_text(
        "\n".join(
            [
                "contract_version: '2.0'",
                "column_count: 0",
                "allow_extra_columns: false",
                "max_duplicate_rate: 0.05",
                "min_completeness_score: 0.95",
                "columns: []",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Unsupported contract version",
    ):
        load_contract_yaml(unsupported_path)


def test_string_boolean_is_rejected(
    tmp_path: Path,
):
    invalid_path = tmp_path / "invalid_boolean.yaml"

    invalid_path.write_text(
        "\n".join(
            [
                "contract_version: '1.0'",
                "column_count: 0",
                "allow_extra_columns: 'false'",
                "max_duplicate_rate: 0.05",
                "min_completeness_score: 0.95",
                "columns: []",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="invalid dataset constraints",
    ):
        load_contract_yaml(invalid_path)


def test_invalid_rate_is_rejected(
    tmp_path: Path,
):
    invalid_path = tmp_path / "invalid_rate.yaml"

    invalid_path.write_text(
        "\n".join(
            [
                "contract_version: '1.0'",
                "column_count: 0",
                "allow_extra_columns: false",
                "max_duplicate_rate: 1.5",
                "min_completeness_score: 0.95",
                "columns: []",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="max_duplicate_rate",
    ):
        load_contract_yaml(invalid_path)


def test_column_count_must_match_declared_columns(
    tmp_path: Path,
):
    invalid_path = tmp_path / "invalid_count.yaml"

    invalid_path.write_text(
        "\n".join(
            [
                "contract_version: '1.0'",
                "column_count: 2",
                "allow_extra_columns: false",
                "max_duplicate_rate: 0.05",
                "min_completeness_score: 0.95",
                "columns:",
                "  - name: customer_id",
                "    dtype: int64",
                "    required: true",
                "    min_completeness: 0.95",
                "    unique: true",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="does not match",
    ):
        load_contract_yaml(invalid_path)
