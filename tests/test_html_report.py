from pathlib import Path

from dataguardian.html_report import generate_html_report
from dataguardian.models import (
    ColumnProfile,
    DatasetProfile,
)


def test_generate_html_report(tmp_path):

    report_file = tmp_path / "report.html"

    profile = DatasetProfile(
        row_count=100,
        column_count=1,
        duplicate_rows=0,
        duplicate_rate=0.0,
        completeness_score=1.0,
        columns=[
            ColumnProfile(
                name="id",
                dtype="int64",
                non_null_count=100,
                null_count=0,
                null_rate=0.0,
                completeness=1.0,
                unique_count=100,
                uniqueness_ratio=1.0,
            )
        ],
        issues=[],
    )

    generate_html_report(
        profile,
        str(report_file),
    )

    assert report_file.exists()

    content = report_file.read_text()

    assert "DataGuardian Quality Report" in content