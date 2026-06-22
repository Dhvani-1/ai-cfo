def build_context(transactions):
    """
    Convert transaction objects into text documents
    suitable for embeddings and retrieval.
    """

    documents = []

    for t in transactions:

        doc = f"""
Date: {t.date}
Description: {t.description}
Amount: {t.amount}
Category: {t.category}
Type: {t.type}
"""

        documents.append(doc.strip())

    return documents