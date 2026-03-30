def generate_verdict(comparison):

    best_doc = None
    best_score = float("inf")

    for doc in list(next(iter(comparison.values())).keys()):

        total_days = 0
        valid = False

        for clause in comparison.values():

            val = clause.get(doc, "-")

            # skip invalid values
            if val == "-" or val == "N/A":
                continue

            try:
                days = int(val.split()[0])
                total_days += days
                valid = True
            except:
                continue

        # skip docs with no valid data
        if not valid:
            continue

        if total_days < best_score:
            best_score = total_days
            best_doc = doc

    if not best_doc:
        return "No clear verdict could be determined."

    return f"{best_doc} appears more favorable based on key terms."