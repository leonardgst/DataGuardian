from dataclasses import dataclass


@dataclass(slots=True)
class ColumnContract:
    """Contraintes attendues pour une colonne."""

    name: str
    dtype: str
    required: bool
    min_completeness: float
    unique: bool


@dataclass(slots=True)
class DatasetContract:
    """Contrat décrivant la structure attendue d'un dataset."""

    contract_version: str
    column_count: int
    allow_extra_columns: bool
    max_duplicate_rate: float
    min_completeness_score: float
    columns: list[ColumnContract]