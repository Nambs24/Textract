import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")


# --------------------------------------------------
# INTERNAL HELPER
# --------------------------------------------------
def _extract_embeddings(response):
    """
    Gemini can return embeddings in slightly different shapes.
    This function normalises the output.
    """

    if not response:
        raise ValueError("Empty embedding response from Gemini.")

    if "embedding" in response:
        # single embedding
        return response["embedding"]

    if "embeddings" in response:
        # batch embeddings
        return [item["embedding"] for item in response["embeddings"]]

    raise ValueError("Unexpected embedding response format.")


# --------------------------------------------------
# EMBED MULTIPLE TEXTS (FOR CHUNKING / LEGACY USE)
# --------------------------------------------------
def embed_texts(texts: list[str]):

    if not MODEL:
        raise ValueError("EMBEDDING_MODEL not set in .env")

    if not texts:
        return []

    response = genai.embed_content(
        model=MODEL,
        content=texts,
        task_type="retrieval_document",
    )

    embeddings = _extract_embeddings(response)

    if not isinstance(embeddings, list):
        raise ValueError("Batch embedding did not return a list.")

    return embeddings


# --------------------------------------------------
# ✅ EMBED SINGLE TEXT (FOR PROFILE UPSERT)
# --------------------------------------------------
def embed_text(text: str):
    """
    Used for:
    - GitHub full profile
    - Resume full profile

    Returns ONE 3072-d vector.
    """

    if not text:
        raise ValueError("Cannot embed empty text.")

    response = genai.embed_content(
        model=MODEL,
        content=text,
        task_type="retrieval_document",
    )

    embedding = _extract_embeddings(response)

    if isinstance(embedding, list) and isinstance(embedding[0], float):
        return embedding

    raise ValueError("Single embedding returned in unexpected format.")


# --------------------------------------------------
# EMBED QUERY (FOR SEARCH)
# --------------------------------------------------
def embed_query(query: str):

    if not query:
        raise ValueError("Query is empty.")

    response = genai.embed_content(
        model=MODEL,
        content=query,
        task_type="retrieval_query",
    )

    embedding = _extract_embeddings(response)

    if isinstance(embedding, list) and isinstance(embedding[0], float):
        return embedding

    raise ValueError("Query embedding returned in unexpected format.")