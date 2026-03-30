import spacy
import re

       
# LOAD MODEL ONCE (IMPORTANT)
       
nlp = spacy.load("en_core_web_sm")


       
# EXTRACT PARTIES (ORG)
       
def extract_parties_spacy(full_text: str):

    intro_text = full_text[:2000]  # only intro

    doc = nlp(intro_text)

    freq = {}

    for ent in doc.ents:

        if ent.label_ != "ORG":
            continue

        val = ent.text.strip()

        # remove junk
        if len(val) < 4:
            continue

        if any(x in val.lower() for x in [
            "section", "article", "agreement", "clause",
            "date", "term", "authority", "board",
            "plan", "transaction"
        ]):
            continue

        # boost company-like names
        score = 1
        if any(suffix in val.lower() for suffix in [
            "inc", "llc", "ltd", "corp", "corporation"
        ]):
            score += 2

        freq[val] = freq.get(val, 0) + score

    sorted_parties = sorted(freq.items(), key=lambda x: x[1], reverse=True)

    return [p[0] for p in sorted_parties[:3]]

       
# MAIN ENTITY EXTRACTOR (HYBRID)
       
def extract_entities_spacy(text: str, doc_parties = None):

    entities = []
    seen = set()

    parties = doc_parties or []

    text_lower = text.lower()

           
    # MONEY
           
    money_pattern = r'(\$[\d,]+(?:\.\d+)?|\d+(?:\.\d+)?\s*(?:million|billion|usd|dollars))'
    for m in re.findall(money_pattern, text_lower):

        if "$" in m:
            num = int(re.sub(r"[^\d]", "", m) or 0)
            if num < 1000:
                continue

        val = m.strip()

        if val not in seen:
            seen.add(val)

            entities.append({
                "type": "Payment",
                "label": "Amount",
                "value": val,
                "parties": parties
            })

           
    # DURATION
           
    duration_pattern = r'(\d+\s*(?:day|days|month|months|year|years))'
    for d in re.findall(duration_pattern, text_lower):

        val = d.strip()

        if val not in seen:
            seen.add(val)

            entities.append({
                "type": "Contract Term",
                "label": "Duration",
                "value": val,
                "parties": parties
            })

           
    # PERCENTAGE
           
    percent_pattern = r'(\d+%)'
    for p in re.findall(percent_pattern, text):

        val = p.strip()

        if val not in seen:
            seen.add(val)

            entities.append({
                "type": "Financial",
                "label": "Percentage",
                "value": val,
                "parties": parties
            })

    return entities