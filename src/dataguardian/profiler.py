import pandas as pd

from dataguardian.models import ColumnProfile, DatasetProfile


def profile_dataframe(df: pd.DataFrame) -> DatasetProfile:
    """
    Analyse un DataFrame et retourne son profil.
    """

    row_count = len(df)
    column_count = len(df.columns)
    duplicate_rows = int(df.duplicated().sum())

    column_profiles: list[ColumnProfile] = []

    for column_name in df.columns:
        series = df[column_name]

        non_null_count = int(series.notna().sum())
        null_count = int(series.isna().sum())

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
                unique_count=unique_count,
                uniqueness_ratio=round(uniqueness_ratio, 4),
            )
        )

    return DatasetProfile(
        row_count=row_count,
        column_count=column_count,
        duplicate_rows=duplicate_rows,
        columns=column_profiles,
    )