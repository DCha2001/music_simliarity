import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy import create_engine, Table, MetaData, text
from youtube import track_to_embeddings
from pgvector.sqlalchemy import Vector

DATABASE_URL = 'postgresql://postgres:DCha@localhost:5432/musicdb'
engine = create_engine(DATABASE_URL)
metadata = MetaData()
songs = Table("songs", metadata, autoload_with=engine)

file_path = 'top_genre_tracks.json'

def get_json_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def process_song(song):
    """Download, embed, return prepared DB row."""
    try:
        embeddings = track_to_embeddings(song["artist"], song["title"])
        if embeddings is None:
            raise Exception

        return {
            "title": song["title"],
            "artist": song["artist"],
            "embedding": embeddings
        }
    except Exception as e:
        print(f"Error processing {song}: {e}")
        return None

def populate_db():
    all_music = get_json_file(file_path)

    results = []
    # Run downloads/embeddings in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_song = {executor.submit(process_song, song): song for song in all_music}
        for future in as_completed(future_to_song):
            result = future.result()
            if result:
                results.append(result)

    # Insert into DB (single transaction)
    with engine.begin() as conn:
        for row in results:
            conn.execute(songs.insert().values(**row))

    print(f"Inserted {len(results)} songs")

if __name__ == "__main__":
    populate_db()