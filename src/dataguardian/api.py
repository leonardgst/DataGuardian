import pandas as pd

from dataguardian.models import DatasetProfile
from dataguardian.profiler import profile_dataframe as _profile_dataframe


def profile_dataframe(df: pd.DataFrame) -> DatasetProfile:
    """
    Point d'entrée public de la librairie.
    """

    return _profile_dataframe(df)