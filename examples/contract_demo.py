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
