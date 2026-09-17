import pandas as pd

from dataguardian import profile_dataframe
from dataguardian.report import save_summary_json

df = pd.read_csv("examples/dirty_customers.csv")

profile = profile_dataframe(df)

print("\nIssues found:")
for issue in profile.issues:
    print(issue)

save_summary_json(profile, "summary.json")

print("\nsummary.json generated successfully")