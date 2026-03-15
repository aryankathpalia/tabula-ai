# app/services/risk_intelligence/language_refiner.py

from typing import Dict


def generate_executive_assessment(
    exposure_level: str,
    dominant_category: str,
    structural_flags: list
) -> str:

    # ------------------------------
    # Base Exposure Framing
    # ------------------------------
    if exposure_level == "High Exposure":
        base = (
            "The agreement presents elevated financial and operational exposure"
        )
    elif exposure_level == "Moderate Exposure":
        base = (
            "The agreement demonstrates measurable legal and financial exposure"
        )
    else:
        base = (
            "The agreement reflects a controlled and comparatively limited risk structure"
        )

    # ------------------------------
    # Dominant Risk Driver
    # ------------------------------
    if dominant_category:
        driver = (
            f", primarily driven by {dominant_category.lower()} allocations"
        )
    else:
        driver = ""

    # ------------------------------
    # Structural Amplifier
    # ------------------------------
    if structural_flags:
        structural_note = (
            ", with additional structural considerations requiring review."
        )
    else:
        structural_note = "."

    return base + driver + structural_note