from dataclasses import dataclass


@dataclass(slots=True)
class ColumnProfile:
    """Profil d'une colonne."""

    name: str
    dtype: str
    non_null_count: int
    null_count: int
    unique_count: int
    uniqueness_ratio: float


@dataclass(slots=True)
class DatasetProfile:
    """Profil global d'un dataset."""

    row_count: int
    column_count: int
    duplicate_rows: int
    columns: list[ColumnProfile]