from fastapi import APIRouter, UploadFile, File
from typing import List
import os
import time
import re
from collections import defaultdict
import fitz

from app.services.contract_comparison.compare import build_comparison
from app.services.contract_comparison.verdict import generate_verdict
from app.services.transformer_compare import get_compare_classifier

from app.services.contract_comparison.spacy_ner import (
    extract_entities_spacy,
    extract_parties_spacy
)


router = APIRouter(prefix="/compare", tags=["Compare"])

classifier = get_compare_classifier()


def debug_block(title, items, limit=3):
    pass  # disabled


def clean_text(text: str):
    text = re.sub(r'Page\s+\d+\s+of\s+\d+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\n+', '\n', text)
    return text.strip()


def extract_text_fixed(path: str):
    doc = fitz.open(path)
    full_text = ""

    for page in doc:
        blocks = page.get_text("blocks")

        for b in blocks:
            block_text = b[4].strip()
            if block_text:
                full_text += block_text + "\n"

    return full_text


def split_into_clauses(text: str):

    text = clean_text(text)
    lines = text.split("\n")

    clauses = []
    buffer = ""

    for line in lines:
        line = line.strip()

        if not line:
            continue

        buffer += " " + line

        if re.match(r'^[a-zA-Z]\.$', line):
            continue

        if re.match(r'^\d+\.$', line):
            continue

        if line.endswith("."):
            if len(buffer.strip()) > 40:
                clauses.append(buffer.strip())
            buffer = ""

    if len(buffer.strip()) > 40:
        clauses.append(buffer.strip())

    return clauses


IMPORTANT_TERMS = [
    "liability", "termination", "indemnity", "payment",
    "confidential", "warranty", "damages", "governing law",
    "insurance", "audit", "ownership", "assignment"
]


    
# SMART LIMIT CLAUSE
    
def limit_clause(text: str, max_tokens=200):

    words = text.split()

    if len(words) <= max_tokens:
        return text

    truncated = " ".join(words[:max_tokens])

    # try to cut at sentence end
    last_period = truncated.rfind(".")
    if last_period > 100:
        return truncated[:last_period + 1]

    # fallback: comma
    last_comma = truncated.rfind(",")
    if last_comma > 100:
        return truncated[:last_comma]

    return truncated

def is_relevant(clause: str):
    c = clause.lower()

    if len(c.split()) < 10:
        return False

    if any(term in c for term in IMPORTANT_TERMS):
        return True

    if len(c.split()) > 40:
        return True

    return False


# Process File (WITH TIMING)
async def process_file(file: UploadFile):

    start_time = time.time()

    content = await file.read()
    temp_path = f"temp_{file.filename}"

    with open(temp_path, "wb") as f:
        f.write(content)

    #   EXTRACT  
    t0 = time.time()
    raw_text = extract_text_fixed(temp_path)
    doc_parties = extract_parties_spacy(raw_text)
    t1 = time.time()
    print(f"Extract: {round(t1 - t0, 2)}s")

    #   CLEAN  
    t2 = time.time()
    cleaned_text = clean_text(raw_text)
    t3 = time.time()
    print(f"Clean: {round(t3 - t2, 2)}s")

    #   SPLIT  
    t4 = time.time()
    clauses = split_into_clauses(cleaned_text)
    t5 = time.time()
    print(f"Split: {round(t5 - t4, 2)}s")

    #   FILTER  
    t6 = time.time()
    filtered = [c for c in clauses if is_relevant(c)]
    t7 = time.time()
    print(f"Filter: {round(t7 - t6, 2)}s")

    valid = []

    # CLASSIFY (batched + limited) 
    t8 = time.time()

    BATCH_SIZE = 4  # safe for CPU (can try 6 later)

    for i in range(0, len(filtered), BATCH_SIZE):

        batch = filtered[i:i + BATCH_SIZE]

        # limit clause size BEFORE model
        batch_clean = [limit_clause(c.strip()) for c in batch]

        preds = classifier.predict(batch_clean)

        for clause_text, pred in zip(batch, preds):

            if pred["confidence"] < 0.6:
                continue

            clause_clean = clause_text.strip()

            # NER EXTRACTION HERE
            entities = extract_entities_spacy(clause_clean, doc_parties)

            valid.append({
                "text": clause_clean,
                "label": pred["label"],
                "doc": file.filename,
                "entities": entities   
            })

    t9 = time.time()
    print(f"Classify (batched): {round(t9 - t8, 2)}s")

    #   GROUP  
    t10 = time.time()

    label_groups = defaultdict(list)

    for c in valid:
        label_groups[c["label"]].append(c)

    final_output = []

    for label, items in label_groups.items():
        items = sorted(items, key=lambda x: len(x["text"]), reverse=True)
        final_output.extend(items[:2])

    t11 = time.time()
    print(f"Group + Select: {round(t11 - t10, 2)}s")

    os.remove(temp_path)

    print(f"FILE DONE: {round(time.time() - start_time, 2)}s")

    return file.filename, final_output



# MAIN ROUTE (WITH TIMING)

@router.post("/")
async def compare_contracts(files: List[UploadFile] = File(...)):

    total_start = time.time()

    if len(files) < 2:
        return {"error": "Upload at least 2 documents"}

    results = []

    # PROCESS FILES 
    t0 = time.time()
    for f in files:
        result = await process_file(f)
        results.append(result)
    t1 = time.time()
    print(f"All files processed: {round(t1 - t0, 2)}s")

    #   GROUP  
    t2 = time.time()
    grouped = defaultdict(list)
    doc_names = []

    for doc_name, clauses in results:
        doc_names.append(doc_name)

        for c in clauses:
            grouped[c["label"]].append(c)
    t3 = time.time()
    print(f"Grouping: {round(t3 - t2, 2)}s")

    #   BUILD COMPARISON  
    t4 = time.time()
    comparison = build_comparison(grouped, doc_names)
    t5 = time.time()
    print(f"Comparison build: {round(t5 - t4, 2)}s")

    #   VERDICT  
    t6 = time.time()
    verdict = generate_verdict(comparison)
    t7 = time.time()
    print(f"Verdict: {round(t7 - t6, 2)}s")

    print(f"TOTAL TIME: {round(time.time() - total_start, 2)}s")

    return {
        "documents": doc_names,
        "comparison": comparison,
        "grouped": grouped,   
        "verdict": verdict
    }