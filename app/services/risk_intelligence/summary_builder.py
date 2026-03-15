# app/services/risk_intelligence/summary_builder.py

from typing import Dict
from .weights import compute_weighted_score, CATEGORY_WEIGHTS
from .exposure import determine_exposure_profile
from .pattern_analyzer import detect_risk_patterns
from .language_refiner import generate_executive_assessment
from .clause_coverage import analyze_clause_coverage
import re

def clean_clause_preview(text: str) -> str:
    text = text.strip()

    # Fix PDF hyphen breaks
    text = re.sub(r'-\s*\n\s*', '', text)

    # Replace newlines with space
    text = re.sub(r'\r?\n+', ' ', text)

    # Collapse multiple spaces
    text = re.sub(r'\s{2,}', ' ', text)

    # Remove leading numbering
    text = re.sub(r'^(ARTICLE\s*[-–]?\s*\d+\.?\s*)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^(\d+(\.\d+)*\s+)', '', text)
    text = re.sub(r'^(\d+\.\s*)', '', text)
    text = re.sub(r'^\s*\(?\d+[\.\)]\s*', '', text)



    return text.strip()


def compute_risk_stability(category_breakdown: Dict, total_score: float) -> Dict:
    """
    Determines how concentrated the risk is across categories.
    """

    if not category_breakdown or total_score == 0:
        return {
            "stability_label": "Insufficient Data",
            "dominance_percent": 0
        }

    # Find highest weighted category
    highest = max(
        category_breakdown.items(),
        key=lambda x: x[1]["weighted_score"]
    )

    dominant_category = highest[0]
    dominant_score = highest[1]["weighted_score"]

    dominance_percent = round((dominant_score / total_score) * 100, 1)

    # Stability Classification
    if dominance_percent >= 70:
        stability_label = "Highly Concentrated (Volatile Risk Structure)"
    elif dominance_percent >= 40:
        stability_label = "Moderately Concentrated"
    else:
        stability_label = "Diversified Risk Distribution"

    return {
        "stability_label": stability_label,
        "dominant_category": dominant_category,
        "dominance_percent": dominance_percent
    }



def build_enterprise_summary(clause_analysis: Dict) -> str:
    """
    Generates structured enterprise-grade legal summary
    using:
        - Weighted scoring
        - Exposure classification
        - Clause distribution analysis
        - Structural risk pattern detection
    """

    if not clause_analysis:
        return "No clause data available for analysis."

    # -----------------------------------------------------
    # STEP 1 — Compute Weighted Risk
    # -----------------------------------------------------
    weighted_output = compute_weighted_score(clause_analysis)

    total_score = weighted_output["total_weighted_score"]
    dominant_category = weighted_output["dominant_category"]
    concentration_ratio = weighted_output["concentration_ratio"]
    category_breakdown = weighted_output["category_breakdown"]


    raw_score = weighted_output["raw_weighted_score"]

    dominant_percentage = 0
    if dominant_category and raw_score > 0:
        dominant_weight = category_breakdown[dominant_category]["weighted_score"]
        dominant_percentage = round((dominant_weight / raw_score) * 100, 1)


    # -----------------------------------------------------
    # STEP 2B — Risk Driver Narrative
    # -----------------------------------------------------
    primary_driver_lines = []

    if dominant_category and dominant_percentage > 0:
        primary_driver_lines.append(
            f"{dominant_category} provisions account for approximately "
            f"{dominant_percentage}% of total weighted contractual risk exposure."
        )

    # Optional: Add second largest contributor
    sorted_categories = sorted(
        category_breakdown.items(),
        key=lambda x: x[1]["weighted_score"],
        reverse=True
    )

    if len(sorted_categories) > 1:
        second_category, second_data = sorted_categories[1]
        second_percentage = round(
            (second_data["weighted_score"] / raw_score) * 100, 1
        ) if raw_score > 0 else 0

        primary_driver_lines.append(
            f"{second_category} clauses contribute an additional "
            f"{second_percentage}% of exposure."
        )

    primary_driver_section = "\n".join(
        [f"- {line}" for line in primary_driver_lines]
    )    

    # -----------------------------------------------------
    # STEP 2 — Determine Exposure Profile
    # -----------------------------------------------------
    exposure_profile = determine_exposure_profile(weighted_output)

    exposure_level = exposure_profile["exposure_level"]
    risk_posture = exposure_profile["risk_posture"]
    risk_concentration = exposure_profile["risk_concentration"]
    


    # -----------------------------------------------------
    # STEP 3 — Structural Pattern Detection
    # -----------------------------------------------------
    pattern_output = detect_risk_patterns(clause_analysis)

    structural_flags = pattern_output["flags"]
    structural_summary = pattern_output["pattern_summary"]


    refined_assessment = generate_executive_assessment(
    exposure_level=exposure_level,
    dominant_category=dominant_category,
    structural_flags=structural_flags
)
    
    coverage_output = analyze_clause_coverage(clause_analysis)
    coverage_ratio = coverage_output["coverage_ratio"]
    coverage_commentary = coverage_output["coverage_commentary"]

    if structural_flags:
        structural_section = "\n".join(
            [f"- {flag}" for flag in structural_flags]
        )
    else:
        structural_section = structural_summary

    # -----------------------------------------------------
    # STEP 4 — Risk Stability Analysis
    # -----------------------------------------------------
    stability_output = compute_risk_stability(
        category_breakdown,
        weighted_output["raw_weighted_score"]
    )

    stability_label = stability_output["stability_label"]
    dominance_percent = stability_output["dominance_percent"]

    # -----------------------------------------------------
    # STEP 4 — Count Clauses
    # -----------------------------------------------------
    total_clauses = sum(len(v) for v in clause_analysis.values())

    # -----------------------------------------------------
    # STEP 5 — Format Category Table
    # -----------------------------------------------------
    category_lines = []

    for category, data in sorted(
        category_breakdown.items(),
        key=lambda x: x[1]["weighted_score"],
        reverse=True
    ):
        line = (
            f"- {category}: "
            f"{data['count']} clauses | "
            f"Weighted Impact: {round(data['weighted_score'], 2)}"
        )
        category_lines.append(line)

    category_section = "\n".join(category_lines)

    # -----------------------------------------------------
    # STEP 6 — Extract Top 3 Most Critical Clauses
    # (True Impact = confidence × category_weight)
    # -----------------------------------------------------

    top_clauses = []

    for category, clauses in clause_analysis.items():

        category_weight = CATEGORY_WEIGHTS.get(category, 3)

        for clause in clauses:
            confidence = clause.get("confidence", 0)
            impact_score = confidence * category_weight

            raw_text = clause.get("clause_text", "")

            # --- Clean structure ---
            cleaned = clean_clause_preview(raw_text)



            # --- Normalize ALL CAPS safely ---
            letters = re.findall(r'[A-Za-z]', cleaned)
            uppercase_ratio = (
                sum(1 for c in letters if c.isupper()) / len(letters)
                if letters else 0
            )

            if uppercase_ratio > 0.7:
                cleaned = cleaned.lower()
                sentences = re.split(r'(?<=[.!?])\s+', cleaned)
                cleaned = " ".join(s.capitalize() for s in sentences)

            top_clauses.append((impact_score, cleaned))


    top_clauses_sorted = sorted(
        top_clauses,
        key=lambda x: x[0],
        reverse=True
    )[:3]


    clause_section = ""

    for i, (_, text) in enumerate(top_clauses_sorted, 1):
        clause_section += f"{i}. {text.strip()}\n\n"
    # -----------------------------------------------------
    # STEP 7 — Final Structured Summary
    # -----------------------------------------------------
    # -----------------------------------------------------
# STEP 7 — Final Structured Summary (NO triple quotes)
# -----------------------------------------------------

    summary = (
    f"## Executive Summary\n\n"
    f"This agreement contains **{total_clauses}** risk-classified clauses.\n\n"
    f"---\n\n"
    f"### Overall Risk Profile\n\n"
    f"- **Overall Risk Score:** {round(total_score, 2)}\n"
    f"- **Exposure Level:** {exposure_level}\n"
    f"- **Risk Posture:** {risk_posture}\n"
    f"- **Risk Concentration:** {risk_concentration}\n\n"
    f"---\n\n"
    f"### Assessment\n\n"
    f"{refined_assessment}\n\n"
    f"---\n\n"
    f"## Structural Risk Signals\n\n"
    f"{structural_section}\n\n"
    f"---\n\n"
    f"## Primary Risk Drivers\n\n"
    f"{primary_driver_section}\n\n"
    f"---\n\n"
    f"## Risk Stability Indicator\n\n"
    f"- **Dominant Category Contribution:** {dominance_percent}%\n"
    f"- **Structure Classification:** {stability_label}\n\n"
    f"---\n\n"
    f"## Risk Distribution Breakdown\n\n"
    f"{category_section}\n\n"
    f"---\n\n"
    f"## Clause Coverage Analysis\n\n"
    f"- **Coverage Ratio:** {coverage_ratio}\n\n"
    f"{coverage_commentary}\n\n"
    f"---\n\n"
    f"## Key High-Impact Clauses\n\n"
    f"{clause_section.strip()}"
    )

    return {
        "overall_score": round(total_score, 2),
        "exposure_level": exposure_level,
        "risk_posture": risk_posture,
        "risk_concentration": risk_concentration,
        "summary_markdown": summary
    }