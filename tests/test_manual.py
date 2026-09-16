import pandas as pd

from dataguardian import profile_dataframe

df = pd.DataFrame(
    {
        "id": [1, 2, 3, 3],
        "name": ["Alice", "Bob", None, "David"],
    }
)

profile = profile_dataframe(df)

print(profile)