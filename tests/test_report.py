import pandas as pd

from dataguardian import profile_dataframe
from dataguardian.report import save_summary_json


def test_save_summary_json(tmp_path):

    df = pd.DataFrame(
        {
            "id": [1, 2, 3]
        }
    )

    profile = profile_dataframe(df)

    output_file = tmp_path / "summary.json"

    save_summary_json(
        profile,
        str(output_file),
    )

    assert output_file.exists()