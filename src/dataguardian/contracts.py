from dataclasses import dataclass
from typing import Any


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


@dataclass(slots=True)
class ContractViolation:
    """Violation détectée pendant la validation d'un contrat."""

    code: str
    severity: str
    column: str | None
    expected: Any
    observed: Any
    message: str


@dataclass(slots=True)
class ValidationResult:
    """Résultat de la validation d'un dataset."""

    violations: list[ContractViolation]

    @property
    def is_valid(self) -> bool:
        """Indique si le dataset respecte entièrement le contrat."""

        return len(self.violations) == 0

    @property
    def violation_count(self) -> int:
        """Retourne le nombre total de violations."""

        return len(self.violations)
