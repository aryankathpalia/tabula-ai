from fastapi import APIRouter
from collections import defaultdict

from app.services.contract_comparison.verdict import generate_verdict
from app.services.risk_intelligence.weights import CATEGORY_WEIGHTS


router = APIRouter(prefix="/compare/insights", tags=["Compare Insights"])


   
# COMPUTE DOC SCORES
   
def compute_doc_scores(grouped, doc_names):

    doc_scores = {doc: 0 for doc in doc_names}
    doc_entities = {doc: [] for doc in doc_names}

    for label, clauses in grouped.items():

        weight = CATEGORY_WEIGHTS.get(label, 3)

        for c in clauses:

            doc = c["doc"]
            confidence = c.get("confidence", 0.7)

            # base score
            doc_scores[doc] += weight * confidence

            # collect entities (FLAT LIST)
            if c.get("entities") and isinstance(c["entities"], list):
                doc_entities[doc].extend(c["entities"])

    return doc_scores, doc_entities


def shorten_name(name: str):
    return name[:25] + "..." if len(name) > 30 else name


   
# ENTITY PENALTY LOGIC
   
def adjust_scores_with_ner(doc_scores, doc_entities):

    for doc, entities_list in doc_entities.items():

        for ent in entities_list:

            value = ent.get("value", "")

            # financial penalty
            if ent["type"] == "Payment":
                if "m" in value.lower() or "$" in value:
                    doc_scores[doc] -= 2

            # percentage penalty
            if ent["type"] == "Financial":
                try:
                    num = int(value.replace("%", ""))
                    if num > 10:
                        doc_scores[doc] -= 2
                except:
                    pass

            # duration penalty
            if ent["type"] == "Contract Term":
                if "year" in value.lower():
                    doc_scores[doc] -= 1

    return doc_scores


   
# GENERATE SMART VERDICT
   
def generate_smart_verdict(doc_scores):

    sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)

    if len(sorted_docs) < 2:
        return "Not enough data for comparison."

    best_doc_full = sorted_docs[0][0]
    best_doc = shorten_name(best_doc_full)

    return f"{best_doc} appears more favorable based on clause risk and financial exposure."


   
# MAIN ROUTE
   
@router.post("/")
async def compare_insights(payload: dict):

    grouped = payload.get("grouped", {})
    doc_names = payload.get("documents", [])

    if not grouped or not doc_names:
        return {"error": "Invalid input"}

    # base scoring
    doc_scores, doc_entities = compute_doc_scores(grouped, doc_names)

    # adjust with NER
    doc_scores = adjust_scores_with_ner(doc_scores, doc_entities)

    # verdict
    verdict = generate_smart_verdict(doc_scores)

    return {
        "doc_scores": doc_scores,
        "entities": doc_entities,
        "verdict": verdict
    }