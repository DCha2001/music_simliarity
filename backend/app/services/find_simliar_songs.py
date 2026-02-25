import json
from sqlalchemy import create_engine, Table, MetaData, text
from pgvector.sqlalchemy import Vector

def find_similar_songs(embedding, limit=5):
    embedding_str = "[" + ",".join(str(x) for x in embedding.tolist()) + "]"
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT id, title, artist, embedding <-> :embedding AS distance
                FROM public.songs
                ORDER BY embedding <-> :embedding
                LIMIT :limit
            """),
            {"embedding": embedding_str, "limit": limit}
        )
        return result.fetchall()
