from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def match_clauses(doc_clauses):

    # Flatten all clauses
    all_clauses = []
    for doc in doc_clauses:
        for c in doc["clauses"]:
            all_clauses.append(c)

    embeddings = np.array([c["embedding"] for c in all_clauses])

    sim_matrix = cosine_similarity(embeddings)

    # Simple grouping (threshold based)
    groups = []
    visited = set()

    for i in range(len(all_clauses)):
        if i in visited:
            continue

        group = [all_clauses[i]]
        visited.add(i)

        for j in range(i + 1, len(all_clauses)):
            if sim_matrix[i][j] > 0.75:
                group.append(all_clauses[j])
                visited.add(j)

        groups.append(group)

    return groups