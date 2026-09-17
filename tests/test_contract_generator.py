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

    generate_contract_yaml(
        profile,
        output_path,
    )

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

    generate_contract_yaml(
        profile,
        output_path,
    )

    with output_path.open(
        mode="r",
        encoding="utf-8",
    ) as file:
        content = yaml.safe_load(file)

    assert content["contract_version"] == "1.0"
    assert content["column_count"] == 2
    assert content["allow_extra_columns"] is False
    assert len(content["columns"]) == 2

    assert content["columns"][0]["name"] == "customer_id"
    assert content["columns"][0]["unique"] is True


def test_generate_contract_rejects_invalid_tolerance():
    df = pd.DataFrame(
        {
            "customer_id": [1, 2, 3],
        }
    )

    profile = profile_dataframe(df)

    with pytest.raises(
        ValueError,
        match="completeness_tolerance",
    ):
        generate_contract(
            profile,
            completeness_tolerance=1.5,
        )
