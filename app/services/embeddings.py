from sentence_transformers import SentenceTransformer

_model = None


import torch
torch.set_num_threads(4)

def get_embedding_model():
    global _model

    if _model is None:
        print("Loading embedding model...")
        _model = SentenceTransformer("BAAI/bge-small-en-v1.5")
        print("Embedding model loaded")

    return _model


def embed_text(texts):
    """
    Generate embeddings using E5 model.
    Supports single string OR list of strings.
    """

    model = get_embedding_model()

    # Convert single text to list
    if isinstance(texts, str):
        texts = [texts]

    formatted = []

    for text in texts:
        if text.strip().endswith("?") or len(text.split()) < 15:
            formatted.append("query: " + text)
        else:
            formatted.append("passage: " + text)

    vectors = model.encode(
        formatted,
        normalize_embeddings=True,
        batch_size=32
    )

    return vectors.tolist()