import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()  # will look for .env in current dir

FM_API_KEY = os.getenv("FM_API_KEY")
BASE_URL = os.getenv("BASE_URL")


# pick 30 genres (tags)
GENRES = [
    "pop", "rock", "hiphop", "rap", "jazz", "classical", "edm", "house",
    "techno", "trance", "metal", "punk", "country", "folk", "blues",
    "reggae", "soul", "funk", "rnb", "indie", "alternative", "grunge",
    "kpop", "latin", "salsa", "afrobeat", "dancehall", "dubstep",
    "lofi", "soundtrack"
]

def get_top_tracks_for_genre(genre, limit=100):
    """Fetch top tracks for a given genre from Last.fm"""
    params = {
        "method": "tag.gettoptracks",
        "tag": genre,
        "api_key": FM_API_KEY,
        "format": "json",
        "limit": limit
    }
    resp = requests.get(BASE_URL, params=params)
    if resp.status_code != 200:
        print(f"Error fetching {genre}: {resp.text}")
        return []

    data = resp.json()
    tracks = []
    for item in data.get("tracks", {}).get("track", []):
        track_info = {
            "title": item["name"],
            "artist": item["artist"]["name"],
            "genre": genre,
            "url": item["url"]  # Last.fm track link
        }
        tracks.append(track_info)
    return tracks

def build_dataset(genres, limit=100):
    dataset = []
    for genre in genres:
        print(f"Fetching {limit} tracks for genre: {genre}")
        tracks = get_top_tracks_for_genre(genre, limit)
        dataset.extend(tracks)
        time.sleep(0.25)  # avoid hammering API
    return dataset

if __name__ == "__main__":
    dataset = build_dataset(GENRES, limit=100)

    # save to JSON
    with open("top_genre_tracks.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved {len(dataset)} tracks across {len(GENRES)} genres.")
