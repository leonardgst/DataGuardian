from dataclasses import asdict
import json

from dataguardian.models import DatasetProfile


def profile_to_dict(profile: DatasetProfile) -> dict:
    """
    Convertit un profil en dictionnaire sérialisable.
    """

    return asdict(profile)


def save_summary_json(
    profile: DatasetProfile,
    filepath: str,
) -> None:
    """
    Sauvegarde le profil au format JSON.
    """

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(
            profile_to_dict(profile),
            f,
            indent=4,
            ensure_ascii=False,
        )