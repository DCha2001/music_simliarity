from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy import create_engine, Table, MetaData, text
from pgvector.sqlalchemy import Vector

import os
import pandas as pd

import pdb

DATABASE_URL = 'postgresql://postgres:password@db:5432/musicdb'
engine = create_engine(DATABASE_URL)
metadata = MetaData()
songs = Table("songs", metadata, autoload_with=engine)

file_path = ""#'C:/Users/Name/OneDrive/Desktop/MusicSimilarity/backend/venv/app/data/fma_small'
meta = ""#'C:/Users/Name/OneDrive/Desktop/MusicSimilarity/backend/venv/app/data/fma_metadata/tracks.csv'

def get_fma_dataset(file_path):

    files = []
    for root, dirs, filenames in os.walk(file_path):  # Limit to first 500 for testing
        for f in filenames:
            if f.endswith(".mp3"):
                files.append(os.path.join(root, f))
    
    print(f"Found {len(files)} audio files")
            
    return files

def process_song(song):
    """Download, embed, return prepared DB row."""
    try:

        tracksmetadata = pd.read_csv(meta, header=[0, 1], index_col=0)
        small = tracksmetadata[tracksmetadata['set', 'subset'] == 'small']


        filename = os.path.basename(song)
        name = os.path.splitext(filename)[0]
        track_id = int(name)
        artist = tracksmetadata.loc[track_id, ('artist', 'name')]
        title = tracksmetadata.loc[track_id, ('track', 'title')]

        embeddings = embed(song)
        if embeddings is None:
            raise Exception
        


        return {
            "title": title,
            "artist": artist,
            "embedding": embeddings
        }
    except Exception as e:
        print(f"Error processing {song}: {e}")
        return None

def populate_db():
    all_music = get_fma_dataset(file_path)[:500]  # Limit to first 500 for testing

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