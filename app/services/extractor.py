import fitz  # PyMuPDF
from docx import Document
from pathlib import Path


def extract_text(file_path: str):
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return extract_pdf_with_layout(path)
    elif suffix == ".docx":
        return extract_docx(path)
    else:
        raise ValueError("Unsupported file type")


def extract_pdf_with_layout(path: Path):
    doc = fitz.open(path)

    full_text = ""
    pages_data = []

    for page_number, page in enumerate(doc, start=1):

        # 🔥 FIX: Use logical text instead of blocks
        page_text = page.get_text("text")
        full_text += page_text + "\n"

        # Keep words for bounding boxes
        words = page.get_text("words")
        page_words = []

        for w in words:
            x0, y0, x1, y1, word, *_ = w
            if not word.strip():
                continue
            page_words.append({
                "text": word.strip(),
                "bbox": [x0, y0, x1, y1]
            })

        pages_data.append({
            "page_number": page_number,
            "width": page.rect.width,
            "height": page.rect.height,
            "words": page_words
        })

    return {
        "full_text": full_text.strip(),
        "pages": pages_data
    }


def extract_docx(path: Path):
    doc = Document(path)
    return {
        "full_text": "\n".join(p.text for p in doc.paragraphs),
        "pages": []
    }