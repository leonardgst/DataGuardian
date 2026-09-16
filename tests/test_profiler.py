import pandas as pd

from dataguardian.profiler import profile_dataframe


def test_row_count():
    df = pd.DataFrame(
        {
            "id": [1, 2, 3]
        }
    )

    result = profile_dataframe(df)

    assert result.row_count == 3


def test_column_count():
    df = pd.DataFrame(
        {
            "id": [1, 2],
            "name": ["A", "B"],
        }
    )

    result = profile_dataframe(df)

    assert result.column_count == 2


def test_duplicate_detection():
    df = pd.DataFrame(
        {
            "id": [1, 1],
            "name": ["A", "A"],
        }
    )

    result = profile_dataframe(df)

    assert result.duplicate_rows == 1


def test_null_count():
    df = pd.DataFrame(
        {
            "name": ["A", None, "C"]
        }
    )

    result = profile_dataframe(df)

    column = result.columns[0]

    assert column.null_count == 1
    assert column.non_null_count == 2


def test_uniqueness_ratio():
    df = pd.DataFrame(
        {
            "id": [1, 1, 2, 3]
        }
    )

    result = profile_dataframe(df)

    column = result.columns[0]

    assert column.unique_count == 3
    assert column.uniqueness_ratio == 0.75