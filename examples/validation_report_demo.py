from pathlib import Path
import sys

import pandas as pd

from dataguardian import (
    generate_validation_html_report,
    load_contract_yaml,
    save_validation_json,
    validate_dataframe,
    validation_exit_code,
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

JSON_OUTPUT_FILE = (
    PROJECT_ROOT
    / "artifacts"
    / "validation.json"
)

HTML_OUTPUT_FILE = (
    PROJECT_ROOT
    / "artifacts"
    / "validation_report.html"
)


def run_validation() -> int:
    """
    Exécute le flux complet de validation et génère les rapports.

    Codes retournés :
    - 0 : dataset valide ;
    - 1 : dataset non conforme ;
    - 2 : erreur technique.
    """
    try:
        dataframe = pd.read_csv(INPUT_FILE)
        contract = load_contract_yaml(CONTRACT_FILE)

        result = validate_dataframe(
            dataframe,
            contract,
        )

        save_validation_json(
            result,
            JSON_OUTPUT_FILE,
        )

        generate_validation_html_report(
            result,
            HTML_OUTPUT_FILE,
        )

    except Exception as error:
        print(
            f"Technical validation error: {error}",
            file=sys.stderr,
        )
        return 2

    status = "VALID" if result.is_valid else "INVALID"

    print(f"Validation status: {status}")
    print(f"Violations: {result.violation_count}")
    print(f"Errors: {result.error_count}")
    print(f"Warnings: {result.warning_count}")
    print(f"JSON report: {JSON_OUTPUT_FILE}")
    print(f"HTML report: {HTML_OUTPUT_FILE}")

    return validation_exit_code(result)


def main() -> None:
    """Point d'entrée du script de démonstration."""
    raise SystemExit(run_validation())


if __name__ == "__main__":
    main()
