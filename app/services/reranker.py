from sentence_transformers import CrossEncoder

_model = None


def get_reranker():
    global _model

    if _model is None:
        print("Loading reranker model...")
        _model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        print("Reranker loaded")

    return _model


def rerank_chunks(query: str, chunks: list, top_k: int = 5):

    if not chunks:
        return []

    model = get_reranker()

    pairs = [
        (query, chunk["text"])
        for chunk in chunks
    ]

    scores = model.predict(pairs)

    ranked = sorted(
        zip(chunks, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return [r[0] for r in ranked[:top_k]]