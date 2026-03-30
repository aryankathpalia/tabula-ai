import re

def split_into_clauses(text: str):
    # Splitting by legal patterns 
    clauses = re.split(r'\n|;|\.', text)

    cleaned = []
    for c in clauses:
        c = c.strip()
        if len(c) > 40:  # ignore small junk
            cleaned.append(c)

    return cleaned