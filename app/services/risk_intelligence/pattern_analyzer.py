# app/services/risk_intelligence/pattern_analyzer.py

from typing import Dict, List


def detect_risk_patterns(clause_analysis: Dict[str, List[dict]]) -> Dict:
    """
    Scans classified clauses for structural legal risk signals.

    Returns:
        {
            "flags": List[str],
            "pattern_summary": str
        }
    """

    flags = []

    if not clause_analysis:
        return {
            "flags": [],
            "pattern_summary": "No pattern analysis available."
        }

    all_clauses = []
    for clauses in clause_analysis.values():
        for clause in clauses:
            text = clause.get("clause_text", "").lower()
            all_clauses.append(text)

    full_text = " ".join(all_clauses)

 
    # LIABILITY PATTERNS
 

    if "unlimited liability" in full_text:
        flags.append("Unlimited liability exposure detected.")

    if "cap" not in full_text and "limitation of liability" in full_text:
        flags.append("Limitation of liability clause detected without explicit monetary cap.")

    if "gross negligence" in full_text:
        flags.append("Liability carve-out for gross negligence present.")

 
    # INDEMNIFICATION PATTERNS
 

    if "indemnify" in full_text and "each party" not in full_text:
        flags.append("Potential unilateral indemnification structure detected.")

    if "indemnify each other" in full_text or "mutual indemnification" in full_text:
        flags.append("Mutual indemnification structure detected.")

 
    # TERMINATION PATTERNS
 

    if "terminate for convenience" in full_text:
        flags.append("Termination for convenience provision present.")

    if "immediate termination" in full_text:
        flags.append("Immediate termination rights detected.")

 
    # RENEWAL PATTERNS
 

    if "automatically renew" in full_text or "auto-renew" in full_text:
        flags.append("Automatic renewal clause detected.")

 
    # JURISDICTION PATTERNS
 

    if "governed by the laws of" in full_text:
        flags.append("Governing law clause present.")

 
    # INSURANCE PATTERNS
 

    if "insurance" in full_text and "shall maintain" in full_text:
        flags.append("Mandatory insurance obligations identified.")

    if "insurance" not in full_text:
        flags.append("No explicit insurance obligations detected.")

 
    # Final Summary
 

    if flags:
        pattern_summary = (
            "Structural risk signals identified: "
            + "; ".join(flags)
        )
    else:
        pattern_summary = "No material structural risk patterns detected."

    return {
        "flags": flags,
        "pattern_summary": pattern_summary
    }