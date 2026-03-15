from sqlalchemy.orm import Session
from sqlalchemy import text
from app.services.embeddings import embed_text



# 1️ GLOBAL SEARCH (DOCUMENT LEVEL - TS VECTOR ONLY)
# Used for main search bar



def retrieve_documents(query: str, top_k: int, db: Session):

    sql = text("""
        SELECT id,
               filename,
               ts_rank(search_vector, plainto_tsquery('english', :query)) AS rank,
               ts_headline(
                   'english',
                   extracted_text,
                   plainto_tsquery('english', :query),
                   'StartSel=<mark>, StopSel=</mark>, MaxFragments=2, MinWords=5, MaxWords=20'
               ) AS snippet
        FROM documents
        WHERE search_vector @@ plainto_tsquery('english', :query)
           OR filename ILIKE :like_query
        ORDER BY rank DESC
        LIMIT :top_k
    """)

    results = db.execute(
        sql,
        {
            "query": query,
            "like_query": f"%{query}%",
            "top_k": top_k
        }
    ).fetchall()

    return [
        {
            "document_id": r.id,
            "filename": r.filename,
            "snippet": r.snippet,
            "relevance": round(float(r.rank) * 1000, 2)
        }
        for r in results
    ]


# 2️ RAG / CHATBOT SEARCH (CHUNK LEVEL - VECTOR ONLY)
# Used only inside rag.py

def retrieve_chunks_for_document(
    query: str,
    document_id: int,
    top_k: int,
    db: Session
):

    query_embedding = embed_text(query)[0]

    # convert python list → pgvector string
    query_embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"

    sql = text("""
        SELECT
            dc.id,
            dc.document_id,
            dc.chunk_index,
            dc.text,
            1 - (dc.embedding <=> CAST(:query_embedding AS vector)) AS similarity
        FROM document_chunks dc
        WHERE dc.document_id = :document_id
        ORDER BY dc.embedding <=> CAST(:query_embedding AS vector)
        LIMIT :top_k
    """)

    results = db.execute(
        sql,
        {
            "query_embedding": query_embedding_str,
            "document_id": document_id,
            "top_k": top_k
        }
    ).fetchall()

    chunks = []

    for r in results:

        snippet = r.text[:400] + "..." if len(r.text) > 400 else r.text

        chunks.append({
            "chunk_id": r.id,
            "snippet": snippet,
            "text": r.text
        })

    return chunks