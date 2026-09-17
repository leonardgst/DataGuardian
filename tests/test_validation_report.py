import json
from pathlib import Path

from dataguardian import (
    generate_validation_html_report,
    save_validation_json,
    validation_exit_code,
    validation_result_to_dict,
)
from dataguardian.contracts import (
    ContractViolation,
    ValidationResult,
)


def build_invalid_result() -> ValidationResult:
    """Construit un résultat invalide réutilisable dans les tests."""
    return ValidationResult(
        violations=[
            ContractViolation(
                code="MISSING_COLUMN",
                severity="ERROR",
                column="customer_id",
                expected="column present",
                observed="column missing",
                message=(
                    "Required column 'customer_id' is missing."
                ),
            ),
            ContractViolation(
                code="MAX_DUPLICATE_RATE",
                severity="ERROR",
                column=None,
                expected=0.05,
                observed=0.25,
                message=(
                    "Dataset duplicate rate is above "
                    "the allowed maximum."
                ),
            ),
            ContractViolation(
                code="MIN_COMPLETENESS",
                severity="WARNING",
                column="city",
                expected=0.90,
                observed=0.75,
                message=(
                    "Column 'city' has insufficient completeness."
                ),
            ),
        ]
    )


def test_valid_result_contains_no_violation():
    result = ValidationResult(violations=[])

    assert result.is_valid is True
    assert result.violation_count == 0
    assert result.error_count == 0
    assert result.warning_count == 0
    assert result.violations_by_severity == {}
    assert result.violations_by_code == {}
    assert result.violations_by_column == {}


def test_invalid_result_contains_expected_counts():
    result = build_invalid_result()

    assert result.is_valid is False
    assert result.violation_count == 3
    assert result.error_count == 2
    assert result.warning_count == 1


def test_violations_are_grouped_by_severity():
    result = build_invalid_result()

    assert result.violations_by_severity == {
        "ERROR": 2,
        "WARNING": 1,
    }


def test_violations_are_grouped_by_code():
    result = build_invalid_result()

    assert result.violations_by_code == {
        "MAX_DUPLICATE_RATE": 1,
        "MIN_COMPLETENESS": 1,
        "MISSING_COLUMN": 1,
    }


def test_violations_are_grouped_by_column():
    result = build_invalid_result()

    assert result.violations_by_column == {
        "DATASET": 1,
        "city": 1,
        "customer_id": 1,
    }


def test_validation_result_to_dict_contains_summary():
    result = build_invalid_result()

    content = validation_result_to_dict(result)

    assert content["is_valid"] is False
    assert content["violation_count"] == 3
    assert content["summary"]["by_severity"]["ERROR"] == 2
    assert content["summary"]["by_severity"]["WARNING"] == 1
    assert content["summary"]["by_column"]["DATASET"] == 1
    assert len(content["violations"]) == 3


def test_validation_result_to_dict_serializes_violation():
    result = build_invalid_result()

    content = validation_result_to_dict(result)
    violation = content["violations"][0]

    assert violation["code"] == "MISSING_COLUMN"
    assert violation["severity"] == "ERROR"
    assert violation["column"] == "customer_id"
    assert violation["expected"] == "column present"
    assert violation["observed"] == "column missing"


def test_save_validation_json_creates_file(
    tmp_path: Path,
):
    result = build_invalid_result()
    output_path = (
        tmp_path
        / "reports"
        / "validation.json"
    )

    save_validation_json(
        result,
        output_path,
    )

    assert output_path.exists()


def test_saved_validation_json_contains_expected_content(
    tmp_path: Path,
):
    result = build_invalid_result()
    output_path = tmp_path / "validation.json"

    save_validation_json(
        result,
        output_path,
    )

    with output_path.open(
        mode="r",
        encoding="utf-8",
    ) as file:
        content = json.load(file)

    assert content["is_valid"] is False
    assert content["violation_count"] == 3
    assert content["summary"]["by_severity"] == {
        "ERROR": 2,
        "WARNING": 1,
    }


def test_generate_valid_html_report(
    tmp_path: Path,
):
    result = ValidationResult(violations=[])
    output_path = tmp_path / "validation_report.html"

    generate_validation_html_report(
        result,
        output_path,
    )

    content = output_path.read_text(
        encoding="utf-8",
    )

    assert output_path.exists()
    assert "DataGuardian Validation Report" in content
    assert "VALID" in content
    assert "No contract violation detected." in content


def test_generate_invalid_html_report(
    tmp_path: Path,
):
    result = build_invalid_result()
    output_path = tmp_path / "validation_report.html"

    generate_validation_html_report(
        result,
        output_path,
    )

    content = output_path.read_text(
        encoding="utf-8",
    )

    assert "INVALID" in content
    assert "MISSING_COLUMN" in content
    assert "MAX_DUPLICATE_RATE" in content
    assert "customer_id" in content
    assert "column missing" in content


def test_html_report_escapes_dynamic_content(
    tmp_path: Path,
):
    result = ValidationResult(
        violations=[
            ContractViolation(
                code="INVALID_DTYPE",
                severity="ERROR",
                column="<script>alert(1)</script>",
                expected="<int64>",
                observed="<object>",
                message="<strong>Invalid value</strong>",
            )
        ]
    )
    output_path = tmp_path / "validation_report.html"

    generate_validation_html_report(
        result,
        output_path,
    )

    content = output_path.read_text(
        encoding="utf-8",
    )

    assert "<script>alert(1)</script>" not in content
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in content
    assert "&lt;int64&gt;" in content
    assert "&lt;object&gt;" in content
    assert "&lt;strong&gt;Invalid value&lt;/strong&gt;" in content


def test_validation_exit_code_is_zero_for_valid_result():
    result = ValidationResult(violations=[])

    assert validation_exit_code(result) == 0


def test_validation_exit_code_is_one_for_invalid_result():
    result = build_invalid_result()

    assert validation_exit_code(result) == 1
