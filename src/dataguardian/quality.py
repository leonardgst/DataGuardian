from dataguardian.models import DatasetProfile, QualityIssue


def detect_quality_issues(profile: DatasetProfile) -> list[QualityIssue]:
    """Détecte les principales anomalies qualité."""

    issues: list[QualityIssue] = []

    if profile.duplicate_rate > 0.05:
        issues.append(
            QualityIssue(
                severity="warning",
                column=None,
                message=(
                    f"Duplicate rate is {profile.duplicate_rate:.1%}, "
                    "above threshold (5%)"
                ),
            )
        )

    for column in profile.columns:

        if column.completeness == 0:
            issues.append(
                QualityIssue(
                    severity="error",
                    column=column.name,
                    message="Column is entirely empty",
                )
            )

        elif column.null_rate > 0.20:
            issues.append(
                QualityIssue(
                    severity="warning",
                    column=column.name,
                    message=(
                        f"Null rate is {column.null_rate:.1%}, "
                        "above threshold (20%)"
                    ),
                )
            )

        if column.uniqueness_ratio < 0.10:
            issues.append(
                QualityIssue(
                    severity="warning",
                    column=column.name,
                    message=(
                        f"Uniqueness ratio is "
                        f"{column.uniqueness_ratio:.1%}, "
                        "below threshold (10%)"
                    ),
                )
            )

    return issues