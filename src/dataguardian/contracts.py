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
        return self.violation_count == 0

    @property
    def violation_count(self) -> int:
        """Retourne le nombre total de violations."""
        return len(self.violations)

    @property
    def error_count(self) -> int:
        """Retourne le nombre de violations de niveau ERROR."""
        return self._count_severity("ERROR")

    @property
    def warning_count(self) -> int:
        """Retourne le nombre de violations de niveau WARNING."""
        return self._count_severity("WARNING")

    @property
    def violations_by_severity(self) -> dict[str, int]:
        """Regroupe les violations par niveau de sévérité."""
        summary: dict[str, int] = {}

        for violation in self.violations:
            severity = violation.severity.upper()
            summary[severity] = summary.get(severity, 0) + 1

        return dict(sorted(summary.items()))

    @property
    def violations_by_code(self) -> dict[str, int]:
        """Regroupe les violations par code."""
        summary: dict[str, int] = {}

        for violation in self.violations:
            code = violation.code
            summary[code] = summary.get(code, 0) + 1

        return dict(sorted(summary.items()))

    @property
    def violations_by_column(self) -> dict[str, int]:
        """
        Regroupe les violations par colonne.

        Les violations définies au niveau du dataset sont regroupées
        sous la clé DATASET.
        """
        summary: dict[str, int] = {}

        for violation in self.violations:
            column = (
                violation.column
                if violation.column is not None
                else "DATASET"
            )
            summary[column] = summary.get(column, 0) + 1

        return dict(sorted(summary.items()))

    def _count_severity(
        self,
        severity: str,
    ) -> int:
        """Compte les violations correspondant à une sévérité."""
        normalized_severity = severity.upper()

        return sum(
            1
            for violation in self.violations
            if violation.severity.upper() == normalized_severity
        )