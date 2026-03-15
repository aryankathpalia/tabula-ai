import re
from collections import defaultdict

def mask_pii(text: str):
    mapping = {}
    counters = defaultdict(int)

    def replace_entity(match, label):
        value = match.group(0)

        # If already mapped, reuse key
        for key, original in mapping.items():
            if original == value:
                return key

        counters[label] += 1
        key = f"{label}_{counters[label]}"
        mapping[key] = value
        return key

    # EMAIL
    text = re.sub(
        r'\b[\w\.-]+@[\w\.-]+\.\w+\b',
        lambda m: replace_entity(m, "EMAIL"),
        text
    )

    # AMOUNT
    text = re.sub(
        r'\$\s?\d+(?:,\d{3})*(?:\.\d{2})?',
        lambda m: replace_entity(m, "AMOUNT"),
        text
    )

    # SSN / ID
    text = re.sub(
        r'\b\d{3}-\d{2}-\d{4}\b',
        lambda m: replace_entity(m, "ID"),
        text
    )

    # PERSON (simple heuristic)
    text = re.sub(
        r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',
        lambda m: replace_entity(m, "PERSON"),
        text
    )

    return text, mapping