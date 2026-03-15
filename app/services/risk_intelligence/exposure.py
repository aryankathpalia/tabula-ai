# app/services/risk_intelligence/exposure.py

from typing import Dict


def determine_exposure_profile(weighted_output: Dict) -> Dict:
    """
    Converts weighted risk output into enterprise-grade exposure classification.

    Input:
        weighted_output (from compute_weighted_score)

    Returns:
        {
            "exposure_level": str,
            "risk_posture": str,
            "risk_concentration": str,
            "summary_sentence": str
        }
    """

    total_score = weighted_output.get("total_weighted_score", 0)
    dominant_category = weighted_output.get("dominant_category")
    concentration_ratio = weighted_output.get("concentration_ratio", 0)

  
    # 1️ Exposure Level (Overall Risk Intensity)
  
    if total_score >= 75:
        exposure_level = "High Exposure"
    elif total_score >= 40:
        exposure_level = "Moderate Exposure"
    else:
        exposure_level = "Low Exposure"

  
    # 2️ Risk Concentration Classification
  
    if concentration_ratio >= 0.6:
        risk_concentration = "Highly Concentrated Risk"
    elif concentration_ratio >= 0.35:
        risk_concentration = "Moderately Concentrated Risk"
    else:
        risk_concentration = "Distributed Risk Profile"

  
    # 3️ Risk Posture
  
    if exposure_level == "High Exposure" and concentration_ratio >= 0.6:
        risk_posture = "Material Legal Vulnerability"
    elif exposure_level == "High Exposure":
        risk_posture = "Broad Legal Exposure"
    elif exposure_level == "Moderate Exposure":
        risk_posture = "Manageable but Structurally Sensitive"
    else:
        risk_posture = "Controlled Risk Structure"

  
    # 4️ Executive One-Line Assessment
  
    if dominant_category:
        summary_sentence = (
            f"The agreement reflects {exposure_level.lower()} "
            f"with primary exposure concentrated in {dominant_category} clauses."
        )
    else:
        summary_sentence = "No material risk concentration detected."

    return {
        "exposure_level": exposure_level,
        "risk_posture": risk_posture,
        "risk_concentration": risk_concentration,
        "summary_sentence": summary_sentence
    }