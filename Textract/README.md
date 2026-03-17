docker exec -it pgvector-db psql -U postgres -d ai_vectors

SELECT DISTINCT document_name FROM resume_chunks;

SELECT id, chunk_text
FROM resume_chunks
WHERE document_name = 'doc_name';

SELECT document_name, COUNT(*)
FROM resume_chunks
GROUP BY document_name;

SELECT vector_dims(embedding)
FROM resume_chunks
LIMIT 5;