from dataguardian.models import (
    ColumnProfile,
    DatasetProfile,
)
from dataguardian.quality import detect_quality_issues


def test_detect_high_null_rate():

    profile = DatasetProfile(
        row_count=100,
        column_count=1,
        duplicate_rows=0,
        duplicate_rate=0.0,
        completeness_score=0.75,
        columns=[
            ColumnProfile(
                name="email",
                dtype="object",
                non_null_count=75,
                null_count=25,
                null_rate=0.25,
                completeness=0.75,
                unique_count=75,
                uniqueness_ratio=1.0,
            )
        ],
        issues=[],
    )

    issues = detect_quality_issues(profile)

    assert len(issues) == 1
    assert issues[0].severity == "warning"
    assert issues[0].column == "email"


def test_detect_empty_column():

    profile = DatasetProfile(
        row_count=100,
        column_count=1,
        duplicate_rows=0,
        duplicate_rate=0.0,
        completeness_score=0.0,
        columns=[
            ColumnProfile(
                name="phone",
                dtype="object",
                non_null_count=0,
                null_count=100,
                null_rate=1.0,
                completeness=0.0,
                unique_count=0,
                uniqueness_ratio=0.0,
            )
        ],
        issues=[],
    )

    issues = detect_quality_issues(profile)

    assert any(issue.severity == "error" for issue in issues)


def test_detect_duplicate_rate():

    profile = DatasetProfile(
        row_count=100,
        column_count=1,
        duplicate_rows=10,
        duplicate_rate=0.10,
        completeness_score=1.0,
        columns=[],
        issues=[],
    )

    issues = detect_quality_issues(profile)

    assert any(
        "Duplicate rate" in issue.message
        for issue in issues
    )