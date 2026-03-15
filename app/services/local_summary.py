import re
from collections import Counter
from typing import Dict, List


def split_sentences(text: str) -> List[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 40]


def build_structured_section(clause_analysis: Dict) -> str:
    if not clause_analysis:
        return "No risk-relevant clauses detected."

    total_clauses = sum(len(v) for v in clause_analysis.values())

    summary_lines = []
    summary_lines.append("Executive Summary")
    summary_lines.append("------------------")
    summary_lines.append(
        f"The document contains {total_clauses} risk-relevant clauses."
    )
    summary_lines.append("")

    summary_lines.append("Risk Distribution:")
    for category, clauses in clause_analysis.items():
        summary_lines.append(f"- {category}: {len(clauses)} clauses")

    summary_lines.append("")
    return "\n".join(summary_lines)


def build_extractive_section(text: str, top_n: int = 5) -> str:
    sentences = split_sentences(text)

    if not sentences:
        return "No extractable content."

    # Simple importance scoring using word frequency
    words = re.findall(r'\w+', text.lower())
    word_freq = Counter(words)

    sentence_scores = []

    for sentence in sentences:
        score = sum(word_freq.get(word.lower(), 0) for word in sentence.split())
        sentence_scores.append((score, sentence))

    # Sort by score descending
    sentence_scores.sort(reverse=True, key=lambda x: x[0])

    top_sentences = [s for _, s in sentence_scores[:top_n]]

    section = []
    section.append("Key Extracted Clauses")
    section.append("---------------------")

    for idx, sentence in enumerate(top_sentences, 1):
        section.append(f"{idx}. {sentence}")

    return "\n\n".join(section)


def generate_local_summary(document) -> str:
    structured = build_structured_section(document.clause_analysis)
    extractive = build_extractive_section(document.extracted_text)

    return f"{structured}\n\n{extractive}"