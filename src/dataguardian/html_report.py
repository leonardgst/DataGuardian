from pathlib import Path

from dataguardian.models import DatasetProfile


def generate_html_report(
    profile: DatasetProfile,
    filepath: str,
) -> None:
    """
    Génère un rapport HTML simple.
    """

    issues_html = ""

    for issue in profile.issues:
        issues_html += f"""
        <tr>
            <td>{issue.severity.upper()}</td>
            <td>{issue.column or '-'}</td>
            <td>{issue.message}</td>
        </tr>
        """

    columns_html = ""

    for column in profile.columns:
        columns_html += f"""
        <tr>
            <td>{column.name}</td>
            <td>{column.dtype}</td>
            <td>{column.completeness:.1%}</td>
            <td>{column.null_rate:.1%}</td>
            <td>{column.uniqueness_ratio:.1%}</td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>DataGuardian Report</title>

        <style>

        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
        }}

        h1 {{
            color: #1f4e79;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
        }}

        th,
        td {{
            border: 1px solid #cccccc;
            padding: 10px;
        }}

        th {{
            background-color: #efefef;
        }}

        </style>
    </head>

    <body>

        <h1>DataGuardian Quality Report</h1>

        <h2>Dataset Overview</h2>

        <ul>
            <li>Rows: {profile.row_count}</li>
            <li>Columns: {profile.column_count}</li>
            <li>Duplicate Rate: {profile.duplicate_rate:.1%}</li>
            <li>Completeness Score: {profile.completeness_score:.1%}</li>
        </ul>

        <h2>Quality Issues</h2>

        <table>
            <tr>
                <th>Severity</th>
                <th>Column</th>
                <th>Message</th>
            </tr>

            {issues_html}
        </table>

        <h2>Column Metrics</h2>

        <table>
            <tr>
                <th>Column</th>
                <th>Type</th>
                <th>Completeness</th>
                <th>Null Rate</th>
                <th>Uniqueness</th>
            </tr>

            {columns_html}
        </table>

    </body>
    </html>
    """

    Path(filepath).write_text(
        html,
        encoding="utf-8",
    )