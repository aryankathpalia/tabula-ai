from collections import defaultdict
import re

from app.services.reranker import rerank_chunks


     
# CLEAN CLAUSE TEXT
     
def clean_clause_text(text: str):

    text = re.sub(r'Source:.*?\d{4}', '', text)
    text = re.sub(r'^\d+[\.\s]+', '', text)
    text = re.sub(r'^[a-zA-Z]\.\s*', '', text)

    return text.strip()


     
# CLAUSE SCORING (SMART)
     
def clause_score(text: str):

    t = text.lower()
    score = 0

    # positive signals
    if "shall" in t: score += 2
    if "indemnify" in t: score += 3
    if "terminate" in t: score += 2
    if "pay" in t: score += 2
    if "liable" in t: score += 2
    if "insurance" in t: score += 2
    if "governed" in t: score += 2

    # negative signals
    if t.startswith("whereas"): score -= 3
    if t.startswith("exhibit"): score -= 3
    if "in consideration" in t: score -= 2

    # too short
    if len(t.split()) < 8:
        score -= 2

    return score


     
# DETECT PAYMENT CLAUSES
     
def is_payment_clause(text: str):

    t = text.lower()

    keywords = [
        "payment", "pay", "fee", "amount",
        "tax", "invoice", "royalty", "usd", "$"
    ]

    return any(k in t for k in keywords)


     
# SAFE TRUNCATE
     
def safe_truncate(text, max_chars=300):

    if len(text) <= max_chars:
        return text

    truncated = text[:max_chars]

    last_space = truncated.rfind(" ")
    if last_space != -1:
        truncated = truncated[:last_space]

    return truncated.strip() + "..."


     
# SMART SHORTEN
     
def smart_shorten(text: str, max_chars=300):

    text = clean_clause_text(text)

    sentences = re.split(r'(?<=[.])\s+', text)

    for s in sentences:

        s_clean = s.strip()

        if len(s_clean) < 50:
            continue

        return safe_truncate(s_clean, max_chars)

    return safe_truncate(text, max_chars)



def smart_clause_preview(text: str, max_chars=300):
    sentences = re.split(r'(?<=[.])\s+', text)

    # prioritize strong sentences
    for s in sentences:
        s_clean = s.strip().lower()

        if len(s_clean) < 40:
            continue

        if any(k in s_clean for k in [
            "shall", "must", "agree", "liable", "terminate", "pay"
        ]):
            return s.strip()

    # fallback: first meaningful sentence
    for s in sentences:
        if len(s.strip()) > 50:
            return s.strip()

    # fallback: truncate
    if len(text) > max_chars:
        truncated = text[:max_chars]
        last_period = truncated.rfind(".")
        if last_period > 100:
            return truncated[:last_period + 1]
        return truncated + "..."

    return text
     
# SELECT BEST CLAUSE
     
def select_best_clause(label, clauses):

    if not clauses:
        return None

    # 1: SCORE ALL
    scored = [
        (clause_score(c["text"]), c)
        for c in clauses
    ]

    # sort by score
    scored = sorted(scored, key=lambda x: x[0], reverse=True)

    # take top candidates
    top_candidates = [c for _, c in scored[:5]]

    if not top_candidates:
        top_candidates = clauses

    # 2: BETTER QUERY
    QUERY_MAP = {
        "Liability": "indemnification liability damages legal responsibility",
        "Termination": "termination clause ending agreement conditions",
        "Renewal Term": "contract duration renewal term extension period",
        "Audit Rights": "audit rights inspection records verification clause",
        "Governing Law": "governing law jurisdiction legal venue clause",
        "Insurance": "insurance obligation coverage requirement clause",
    }

    query = QUERY_MAP.get(label, f"{label} clause legal agreement obligations")

    # 3: RERANK
    ranked = rerank_chunks(query, top_candidates, top_k=3)

    return ranked[0] if ranked else top_candidates[0]


     
# MAIN BUILD FUNCTION
     
def build_comparison(grouped, doc_names):

    output = {}

    for label, clauses in grouped.items():

        # FIX LABEL CONFUSION
        if label == "Liquidated Damages":

            # check if actually payment
            payment_like = any(is_payment_clause(c["text"]) for c in clauses)

            if payment_like:
                label = "Payment"

        output[label] = {doc: "-" for doc in doc_names}

        doc_map = defaultdict(list)

        for c in clauses:
            doc_map[c["doc"]].append(c)

        for doc in doc_names:

            doc_clauses = doc_map.get(doc, [])

            best = select_best_clause(label, doc_clauses)

            if not best:
                continue

            value = smart_clause_preview(best["text"])

            output[label][doc] = value

                 

                 
            if "Other" in output:
                other_data = output.pop("Other")
                output["Other"] = other_data

    return output