import os
import json
import psycopg2
from dotenv import load_dotenv
from pgvector.psycopg2 import register_vector

from services.embeddings import embed_query

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


class VectorStore:
    def __init__(self):
        self.conn = None

    # --------------------------------------------------
    # INIT DB
    # --------------------------------------------------
    def init_db(self):
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL not set")

        self.conn = psycopg2.connect(DATABASE_URL)
        self.conn.autocommit = True
        register_vector(self.conn)

    def _cursor(self):
        if self.conn is None:
            raise RuntimeError("DB not initialized. Call init_db() first.")
        return self.conn.cursor()

    # --------------------------------------------------
    # UPSERT PROFILE (ONE ROW PER USER)
    # --------------------------------------------------
    def upsert_profile(
        self,
        github_username,
        person,
        content,
        embedding,
        github_repos=None,
        resume=None,
        source=None,
    ):
        sql = """
        INSERT INTO documents
        (github_username, person, content, embedding, github_repos, resume, source)

        VALUES (%s, %s, %s, %s, %s, %s, %s)

        ON CONFLICT (github_username)
        DO UPDATE SET
            person = EXCLUDED.person,
            content = EXCLUDED.content,
            embedding = EXCLUDED.embedding,
            github_repos = COALESCE(EXCLUDED.github_repos, documents.github_repos),
            resume = COALESCE(EXCLUDED.resume, documents.resume),
            source = EXCLUDED.source;
        """

        with self._cursor() as cur:
            cur.execute(
                sql,
                (
                    github_username,
                    person,
                    content,
                    embedding,
                    json.dumps(github_repos) if github_repos else None,
                    resume,
                    source,
                ),
            )

    # --------------------------------------------------
    # SEARCH (UPDATED)
    # --------------------------------------------------
    def similarity_search(self, query: str, github_username: str, top_k=5):

        query_embedding = embed_query(query)

        sql = """
        SELECT
            content,
            jsonb_build_object(
                'person', person,
                'source', source,
                'github_username', github_username
            ) AS metadata,
            1 - (embedding <=> %s::vector) AS score
        FROM documents
        WHERE github_username = %s
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
        """

        with self._cursor() as cur:
            cur.execute(sql, (query_embedding, github_username, query_embedding, top_k))
            return cur.fetchall()


# =========================================================
# SINGLETON
# =========================================================

vectorstore = VectorStore()


# =========================================================
# FUNCTIONS USED BY NODES
# =========================================================

def init_db():
    vectorstore.init_db()


def upsert_profile(**kwargs):
    vectorstore.upsert_profile(**kwargs)


def similarity_search(query: str, github_username: str, top_k=5):
    return vectorstore.similarity_search(query, github_username, top_k)


# --------------------------------------------------
# CHECK IF USER EXISTS
# --------------------------------------------------
def person_exists(github_username: str) -> bool:

    sql = """
    SELECT 1
    FROM documents
    WHERE github_username = %s
    LIMIT 1
    """

    with vectorstore._cursor() as cur:
        cur.execute(sql, (github_username,))
        return cur.fetchone() is not None


# --------------------------------------------------
# STALENESS CHECK
# --------------------------------------------------
def is_stale(github_username: str, days: int = 7) -> bool:
    return False