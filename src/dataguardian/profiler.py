import pandas as pd

from dataguardian.models import ColumnProfile, DatasetProfile
from dataguardian.quality import detect_quality_issues


def profile_dataframe(df: pd.DataFrame) -> DatasetProfile:
    """
    Analyse un DataFrame et retourne son profil.
    """

    row_count = len(df)
    column_count = len(df.columns)
    duplicate_rows = int(df.duplicated().sum())

    duplicate_rate = (
        duplicate_rows / row_count
        if row_count > 0
        else 0.0
    )

    column_profiles: list[ColumnProfile] = []

    total_non_null = 0

    for column_name in df.columns:
        series = df[column_name]

        non_null_count = int(series.notna().sum())
        null_count = int(series.isna().sum())

        total_non_null += non_null_count

        null_rate = (
            null_count / row_count
            if row_count > 0
            else 0.0
        )

        completeness = (
            non_null_count / row_count
            if row_count > 0
            else 0.0
        )

        unique_count = int(series.nunique(dropna=True))

        uniqueness_ratio = (
            unique_count / non_null_count
            if non_null_count > 0
            else 0.0
        )

        column_profiles.append(
            ColumnProfile(
                name=str(column_name),
                dtype=str(series.dtype),
                non_null_count=non_null_count,
                null_count=null_count,
                null_rate=round(null_rate, 4),
                completeness=round(completeness, 4),
                unique_count=unique_count,
                uniqueness_ratio=round(uniqueness_ratio, 4),
            )
        )

    total_cells = row_count * column_count

    completeness_score = (
        total_non_null / total_cells
        if total_cells > 0
        else 0.0
    )

    profile = DatasetProfile(
        row_count=row_count,
        column_count=column_count,
        duplicate_rows=duplicate_rows,
        duplicate_rate=round(duplicate_rate, 4),
        completeness_score=round(completeness_score, 4),
        columns=column_profiles,
        issues=[],
    )

    profile.issues = detect_quality_issues(profile)

    return profile