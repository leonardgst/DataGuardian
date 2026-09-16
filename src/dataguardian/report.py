from dataclasses import asdict

from dataguardian.models import DatasetProfile


def profile_to_dict(profile: DatasetProfile) -> dict:
    """
    Convertit un profil en dictionnaire sérialisable.
    """

    return asdict(profile)