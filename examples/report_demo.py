import pandas as pd

from dataguardian import (
    generate_html_report,
    profile_dataframe,
    save_summary_json,
)

df = pd.read_csv(
    "examples/dirty_customers.csv"
)

profile = profile_dataframe(df)

save_summary_json(
    profile,
    "artifacts/summary.json",
)

generate_html_report(
    profile,
    "artifacts/report.html",
)

print("Report generated successfully.")
