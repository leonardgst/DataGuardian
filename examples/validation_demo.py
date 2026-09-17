from pathlib import Path

import pandas as pd

from dataguardian import (
    load_contract_yaml,
    validate_dataframe,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "examples"
    / "dirty_customers.csv"
)

CONTRACT_FILE = (
    PROJECT_ROOT
    / "artifacts"
    / "contract.yaml"
)


def main() -> None:
    """
    Valide un fichier CSV d'exemple à partir d'un contrat YAML.
    """

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input dataset not found: {INPUT_FILE}"
        )

    if not CONTRACT_FILE.exists():
        raise FileNotFoundError(
            "Contract file not found. Generate it first with: "
            "python examples/contract_demo.py"
        )

    df = pd.read_csv(INPUT_FILE)
    contract = load_contract_yaml(CONTRACT_FILE)

    result = validate_dataframe(
        df,
        contract,
    )

    print("DataGuardian contract validation")
   