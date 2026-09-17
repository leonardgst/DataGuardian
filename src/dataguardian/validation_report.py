from dataclasses import asdict
from html import escape
import json
from pathlib import Path
from typing import Any

from dataguardian.contracts import ValidationResult


def validation_result_to_dict(
    result: ValidationResult,
) -> dict[str, Any]:
    """
    Convertit un résultat de validation en dictionnaire sérialisable.

    Le dictionnaire contient :
    - le statut global ;
    - le nombre total de violations ;
    - une synthèse par sévérité ;
    - une synthèse par code ;
    - une synthèse par colonne ;
    - le détail de chaque violation.
    """
    return {
        "is_valid": result.is_valid,
        "violation_count": result.violation_count,
        "summary": {
            "by_severity": result.violations_by_severity,
            "by_code": result.violations_by_code,
            "by_column": result.violations_by_column,
        },
        "violations": [
            asdict(violation)
            for violation in result.violations
        ],
    }


def save_validation_json(
    result: ValidationResult,
    filepath: str | Path,
) -> None:
    """
    Enregistre un résultat de validation au format JSON.

    Le dossier parent est créé automatiquement s'il n'existe pas.
    """
    output_path = Path(filepath)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        mode="w",
        encoding="utf-8",
    ) as file:
        json.dump(
            validation_result_to_dict(result),
            file,
            indent=4,
            ensure_ascii=False,
        )


def generate_validation_html_report(
    result: ValidationResult,
    filepath: str | Path,
) -> None:
    """
    Génère un rapport HTML autonome à partir d'un résultat de validation.

    Les contenus variables sont échappés afin d'éviter qu'un nom de
    colonne, une valeur ou un message soit interprété comme du HTML.
    """
    output_path = Path(filepath)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    status = "VALID" if result.is_valid else "INVALID"
    status_class = "status-valid" if result.is_valid else "status-invalid"

    severity_rows = _build_summary_rows(
        result.violations_by_severity,
        empty_message="No severity recorded",
    )
    code_rows = _build_summary_rows(
        result.violations_by_code,
        empty_message="No violation code recorded",
    )
    column_rows = _build_summary_rows(
        result.violations_by_column,
        empty_message="No affected column",
    )
    violation_rows = _build_violation_rows(result)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta
        name="viewport"
        content="width=device-width, initial-scale=1"
    >
    <title>DataGuardian Validation Report</title>
    <style>
        :root {{
            --background: #f5f7fa;
            --surface: #ffffff;
            --text: #1f2933;
            --muted: #52606d;
            --border: #d9e2ec;
            --primary: #1f4e79;
            --valid: #177245;
            --valid-background: #e8f5ee;
            --invalid: #b42318;
            --invalid-background: #fef0ed;
            --warning: #8a5b00;
            --warning-background: #fff7df;
        }}

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            padding: 40px;
            background: var(--background);
            color: var(--text);
            font-family: Arial, Helvetica, sans-serif;
        }}

        main {{
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
        }}

        h1,
        h2 {{
            color: var(--primary);
        }}

        h1 {{
            margin-top: 0;
        }}

        .card {{
            padding: 24px;
            margin-bottom: 24px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 10px;
        }}

        .overview {{
            display: grid;
            grid-template-columns: repeat(
                auto-fit,
                minmax(210px, 1fr)
            );
            gap: 16px;
        }}

        .metric {{
            padding: 18px;
            background: var(--background);
            border-radius: 8px;
        }}

        .metric-label {{
            margin-bottom: 8px;
            color: var(--muted);
            font-size: 0.9rem;
        }}

        .metric-value {{
            font-size: 1.5rem;
            font-weight: bold;
        }}

        .status {{
            display: inline-block;
            padding: 8px 14px;
            border-radius: 999px;
            font-weight: bold;
        }}

        .status-valid {{
            color: var(--valid);
            background: var(--valid-background);
        }}

        .status-invalid {{
            color: var(--invalid);
            background: var(--invalid-background);
        }}

        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(
                auto-fit,
                minmax(260px, 1fr)
            );
            gap: 24px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th,
        td {{
            padding: 12px;
            border: 1px solid var(--border);
            text-align: left;
            vertical-align: top;
        }}

        th {{
            background: #edf2f7;
        }}

        .severity-error {{
            color: var(--invalid);
            font-weight: bold;
        }}

        .severity-warning {{
            color: var(--warning);
            font-weight: bold;
        }}

        .empty-message {{
            color: var(--muted);
            font-style: italic;
        }}

        .table-container {{
            overflow-x: auto;
        }}

        @media (max-width: 700px) {{
            body {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <main>
        <div class="card">
            <h1>DataGuardian Validation Report</h1>

            <div class="overview">
                <div class="metric">
                    <div class="metric-label">Validation Status</div>
                    <div class="metric-value">
                        <span class="status {status_class}">
                            {status}
                        </span>
                    </div>
                </div>

                <div class="metric">
                    <div class="metric-label">
                        Total Violations
                    </div>
                    <div class="metric-value">
                        {result.violation_count}
                    </div>
                </div>

                <div class="metric">
                    <div class="metric-label">Errors</div>
                    <div class="metric-value">
                        {result.error_count}
                    </div>
                </div>

                <div class="metric">
                    <div class="metric-label">Warnings</div>
                    <div class="metric-value">
                        {result.warning_count}
                    </div>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>Validation Summary</h2>

            <div class="summary-grid">
                <section>
                    <h3>By Severity</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Severity</th>
                                <th>Count</th>
                            </tr>
                        </thead>
                        <tbody>
                            {severity_rows}
                        </tbody>
                    </table>
                </section>

                <section>
                    <h3>By Code</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Code</th>
                                <th>Count</th>
                            </tr>
                        </thead>
                        <tbody>
                            {code_rows}
                        </tbody>
                    </table>
                </section>

                <section>
                    <h3>By Column</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Column</th>
                                <th>Count</th>
                            </tr>
                        </thead>
                        <tbody>
                            {column_rows}
                        </tbody>
                    </table>
                </section>
            </div>
        </div>

        <div class="card">
            <h2>Violation Details</h2>

            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Severity</th>
                            <th>Code</th>
                            <th>Column</th>
                            <th>Expected</th>
                            <th>Observed</th>
                            <th>Message</th>
                        </tr>
                    </thead>
                    <tbody>
                        {violation_rows}
                    </tbody>
                </table>
            </div>
        </div>
    </main>
</body>
</html>
"""

    output_path.write_text(
        html_content,
        encoding="utf-8",
    )


def validation_exit_code(
    result: ValidationResult,
) -> int:
    """
    Retourne un code de sortie exploitable par une CI.

    Codes :
    - 0 : validation réussie ;
    - 1 : dataset non conforme au contrat.

    Les erreurs techniques doivent être gérées par le code appelant avec
    un code de sortie distinct, par exemple 2.
    """
    return 0 if result.is_valid else 1


def _build_summary_rows(
    summary: dict[str, int],
    *,
    empty_message: str,
) -> str:
    """Construit les lignes HTML d'une table de synthèse."""
    if not summary:
        return (
            '<tr>'
            '<td colspan="2" class="empty-message">'
            f"{escape(empty_message)}"
            "</td>"
            "</tr>"
        )

    rows: list[str] = []

    for label, count in summary.items():
        rows.append(
            "<tr>"
            f"<td>{escape(str(label))}</td>"
            f"<td>{count}</td>"
            "</tr>"
        )

    return "\n".join(rows)


def _build_violation_rows(
    result: ValidationResult,
) -> str:
    """Construit les lignes de la table détaillant les violations."""
    if result.is_valid:
        return (
            '<tr>'
            '<td colspan="6" class="empty-message">'
            "No contract violation detected."
            "</td>"
            "</tr>"
        )

    rows: list[str] = []

    for violation in result.violations:
        severity = str(violation.severity).upper()
        severity_class = _severity_css_class(severity)

        rows.append(
            "<tr>"
            f'<td class="{severity_class}">'
            f"{escape(severity)}"
            "</td>"
            f"<td>{escape(str(violation.code))}</td>"
            f"<td>{_display_value(violation.column)}</td>"
            f"<td>{_display_value(violation.expected)}</td>"
            f"<td>{_display_value(violation.observed)}</td>"
            f"<td>{escape(str(violation.message))}</td>"
            "</tr>"
        )

    return "\n".join(rows)


def _severity_css_class(
    severity: str,
) -> str:
    """Retourne la classe CSS associée à une sévérité."""
    normalized_severity = severity.lower()

    if normalized_severity == "error":
        return "severity-error"

    if normalized_severity == "warning":
        return "severity-warning"

    return ""


def _display_value(
    value: Any,
) -> str:
    """Convertit et échappe une valeur destinée au rapport HTML."""
    if value is None:
        return "-"

    return escape(str(value))