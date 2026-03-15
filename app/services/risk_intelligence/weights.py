# app/services/risk_intelligence/weights.py

from typing import Dict, List



# 1️  Category Severity Weights
# These represent legal severity / financial exposure impact.
# You can tune them later based on domain feedback.

CATEGORY_WEIGHTS: Dict[str, int] = {
    "Liability": 10,
    "Liquidated Damages": 9,
    "Indemnification": 9,   # keep if used
    "Termination": 8,
    "Non-Compete": 8,
    "Non-Solicit": 7,
    "Change Of Control": 7,
    "Ip Ownership Assignment": 7,
    "Confidentiality": 6,
    "Warranty": 6,
    "Insurance": 5,
    "Governing Law": 4,
    "Audit Rights": 4,
    "Renewal Term": 3,
    "Source Code Escrow": 6,
    "Other": 2
}

# 2️ Compute Weighted Risk Score

def compute_weighted_score(clause_analysis: Dict[str, List[dict]]) -> Dict:

    if not clause_analysis:
        return {
            "raw_weighted_score": 0,
            "total_weighted_score": 0,
            "category_scores": {},
            "category_breakdown": {},
            "dominant_category": None,
            "concentration_ratio": 0
        }

    category_scores: Dict[str, float] = {}
    category_breakdown: Dict[str, Dict] = {}
    raw_score = 0

    for category, clauses in clause_analysis.items():

        weight = CATEGORY_WEIGHTS.get(category, 3)

        category_total = 0
        clause_count = len(clauses)

        for clause in clauses:
            confidence = clause.get("confidence", 0)
            importance = confidence * weight
            category_total += importance

        category_total = round(category_total, 2)

        category_scores[category] = category_total

        category_breakdown[category] = {
            "count": clause_count,
            "weighted_score": category_total
        }

        raw_score += category_total

    # Normalize score relative to document size

        total_clauses = sum(len(v) for v in clause_analysis.values())

        max_weight = max(CATEGORY_WEIGHTS.values())

        max_possible_raw_score = total_clauses * max_weight

        if max_possible_raw_score > 0:
            total_weighted_score = round(
                (raw_score / max_possible_raw_score) * 100,
                2
            )
        else:
            total_weighted_score = 0

    dominant_category = None
    if category_scores:
        dominant_category = max(category_scores, key=category_scores.get)

    concentration_ratio = 0
    if raw_score > 0 and dominant_category:
        concentration_ratio = round(
            category_scores[dominant_category] / raw_score,
            2
        )

    return {
        "raw_weighted_score": round(raw_score, 2),
        "total_weighted_score": total_weighted_score,
        "category_scores": category_scores,
        "category_breakdown": category_breakdown,
        "dominant_category": dominant_category,
        "concentration_ratio": concentration_ratio
    }