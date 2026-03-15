import json
import csv
import re

CUAD_PATH = r"C:\Users\NewUser123\Downloads\CUAD_v1\CUAD_v1\CUAD_v1.json"
OUTPUT_PATH = "processed_cuad_with_other.csv"


# Enterprise Legal Clause Categories

ALLOWED_CLAUSES = {
    "Audit Rights",
    "Liability",
    "Liquidated Damages",
    "Governing Law",
    "Insurance",
    "Non-Compete",
    "Non-Solicit",
    "Change Of Control",
    "Termination",
    "Renewal Term",
    "Warranty",
    "Ip Ownership Assignment",
    "Source Code Escrow",
    "Confidentiality"
}

INCLUDE_OTHER_CLASS = True
MAX_OTHER_SAMPLES = 1000   # prevent imbalance


def extract_clause_name(question_text):
    match = re.search(r'"([^"]+)"', question_text)
    if match:
        return match.group(1).strip()
    return None


def normalize_clause_name(name):

    name = name.strip()

    # ---- LIABILITY ----
    if name in ["Cap On Liability", "Uncapped Liability"]:
        return "Liability"

    # ---- NON-SOLICIT ----
    if name in ["No-Solicit Of Employees", "No-Solicit Of Customers"]:
        return "Non-Solicit"

    # ---- TERMINATION ----
    if name in ["Termination For Convenience"]:
        return "Termination"

    # ---- WARRANTY ----
    if name in ["Warranty Duration"]:
        return "Warranty"

    # ---- CONFIDENTIALITY ----
    if name in ["Non-Disparagement"]:
        return "Confidentiality"

    return name


def extract_cuad():
    print("Loading CUAD dataset...")

    with open(CUAD_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = []
    other_count = 0
    all_clause_names = set()

    # Discover all raw labels
    for contract in data["data"]:
        for paragraph in contract["paragraphs"]:
            for qa in paragraph["qas"]:
                clause_name = extract_clause_name(qa["question"])
                if clause_name:
                    all_clause_names.add(clause_name)

    print("\n==============================")
    print("ALL CLAUSE TYPES FOUND IN CUAD:")
    print("==============================\n")
    for name in sorted(all_clause_names):
        print(name)
    print("\nTotal clause types found:", len(all_clause_names))



    # Main Extraction Logic


    for contract in data["data"]:
        for paragraph in contract["paragraphs"]:
            for qa in paragraph["qas"]:

                clause_name = extract_clause_name(qa["question"])
                if not clause_name:
                    continue

                normalized_name = normalize_clause_name(clause_name)

                answers = qa.get("answers", [])

                for ans in answers:
                    clause_text = ans["text"].strip()

                    if len(clause_text.split()) < 12:
                        continue

                    # 1️ If in allowed classes
                    if normalized_name in ALLOWED_CLAUSES:
                        rows.append({
                            "clause_text": clause_text,
                            "label": normalized_name
                        })

                    # 2️ Else: assign to Other
                    elif INCLUDE_OTHER_CLASS and other_count < MAX_OTHER_SAMPLES:
                        rows.append({
                            "clause_text": clause_text,
                            "label": "Other"
                        })
                        other_count += 1

    unique_labels = set([r["label"] for r in rows])

    print(f"Extracted {len(rows)} clauses")
    print(f"Unique labels (final): {len(unique_labels)}")
    print("Labels:", unique_labels)

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["clause_text", "label"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved clean dataset to {OUTPUT_PATH}")


if __name__ == "__main__":
    extract_cuad()
