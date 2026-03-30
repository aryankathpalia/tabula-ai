import re


      
# NORMALIZATION HELPERS
      
def normalize_money(value: str):

    v = value.lower().replace(",", "").strip()

    if "million" in v:
        num = re.findall(r"\d+", v)
        if num:
            return f"{num[0]}M"

    if "billion" in v:
        num = re.findall(r"\d+", v)
        if num:
            return f"{num[0]}B"

    if "$" in v:
        num = re.findall(r"\d+", v)
        if num:
            return f"${num[0]}"

    return value


def normalize_duration(value: str):

    v = value.lower()

    num = re.findall(r"\d+", v)
    if not num:
        return value

    n = int(num[0])

    if "month" in v:
        return f"{round(n/12, 1)} years" if n > 12 else f"{n} months"

    if "day" in v:
        return f"{round(n/30, 1)} months" if n > 30 else f"{n} days"

    return value


      
# CONTEXT DETECTION
      
def detect_context(text: str, clause_label: str = None):

    t = text.lower()

    # Clause-aware override (VERY POWERFUL)
    if clause_label:
        if "liability" in clause_label.lower():
            return "Liability"
        if "payment" in clause_label.lower():
            return "Payment"
        if "termination" in clause_label.lower():
            return "Termination"
        if "non-compete" in clause_label.lower():
            return "Restriction"

    # fallback keyword logic
    if any(k in t for k in ["equity", "ownership", "share"]):
        return "Equity"

    if any(k in t for k in ["payment", "fee", "royalty"]):
        return "Payment"

    if any(k in t for k in ["penalty", "damages", "late fee"]):
        return "Penalty"

    if any(k in t for k in ["liability", "indemnify"]):
        return "Liability"

    if any(k in t for k in ["term", "duration", "period"]):
        return "Contract Term"

    return "General"


      
# PARTY EXTRACTION (BASIC)
      
def extract_parties(text: str):

    parties = []

    # simple patterns
    patterns = [
        r"(licensor)",
        r"(licensee)",
        r"(buyer)",
        r"(seller)",
        r"(party\s[a-z])"
    ]

    for p in patterns:
        matches = re.findall(p, text.lower())
        for m in matches:
            if m not in parties:
                parties.append(m.title())

    return parties


      
# MAIN ENTITY EXTRACTOR
      
def extract_entities_from_text(text: str, clause_label: str = None):

    entities = []
    seen = set()

    context = detect_context(text, clause_label)
    parties = extract_parties(text)

    text_lower = text.lower()

          
    # MONEY
          
    money_pattern = r'(\$[\d,]+(?:\.\d+)?|\d+(?:\.\d+)?\s*(?:million|billion|usd|dollars))'

    for m in re.findall(money_pattern, text_lower):

        # ignore tiny junk values
        if "$" in m:
            num = int(re.sub(r"[^\d]", "", m) or 0)
            if num < 1000:
                continue

        val = normalize_money(m.strip())

        if val not in seen:
            seen.add(val)
            entities.append({
                "type": context,
                "label": "Amount",
                "value": val,
                "raw_type": "Financial",
                "parties": parties
            })

          
    # PERCENTAGE
          
    percent_pattern = r'(\d+%)'

    for p in re.findall(percent_pattern, text):

        val = p.strip()

        if val not in seen:
            seen.add(val)
            entities.append({
                "type": context,
                "label": "Percentage",
                "value": val,
                "raw_type": "Percentage",
                "parties": parties
            })

          
    # DURATION
          
    duration_pattern = r'(\d+\s*(?:day|days|month|months|year|years))'

    for d in re.findall(duration_pattern, text_lower):

        val = normalize_duration(d.strip())

        if val not in seen:
            seen.add(val)
            entities.append({
                "type": context,
                "label": "Duration",
                "value": val,
                "raw_type": "Duration",
                "parties": parties
            })

    return entities