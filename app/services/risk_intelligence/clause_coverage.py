from typing import Dict, List
from .weights import CATEGORY_WEIGHTS


def analyze_clause_coverage(clause_analysis: Dict[str, List[dict]]) -> Dict:
    """
    Measures:
    - Coverage of expected legal clause categories
    - Missing critical clauses
    - Clause density insight
    """

    if not clause_analysis:
        return {
            "coverage_ratio": 0,
            "missing_categories": list(CATEGORY_WEIGHTS.keys()),
            "coverage_commentary": "No clause coverage detected."
        }

    detected_categories = set(clause_analysis.keys())
    expected_categories = set(CATEGORY_WEIGHTS.keys())

    missing_categories = expected_categories - detected_categories

    coverage_ratio = round(
        len(detected_categories) / len(expected_categories),
        2
    )

    # Commentary Logic
    if coverage_ratio >= 0.75:
        commentary = "Broad contractual risk coverage detected."
    elif coverage_ratio >= 0.4:
        commentary = "Moderate structural clause coverage observed."
    else:
        commentary = "Limited contractual protection structure detected."

    return {
        "coverage_ratio": coverage_ratio,
        "missing_categories": sorted(list(missing_categories)),
        "coverage_commentary": commentary
    }