import yt_dlp
import os
import uuid
import openl3
import soundfile as sf

from pathlib import Path

TEMP_DIR = "temp_audio"

def search_youtube_yt_dlp(query, max_results=1):
    try:
        search_url = f"ytsearch{max_results}:{query}"
        ydl_opts = {"quiet": True, "skip_download": True}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_url, download=False)
        
        if not info.get("entries"):
            print("No results found")
            return []

        results = []
        for entry in info["entries"]:
            results.append({
                "title": entry.get("title"),
                "url": entry.get("webpage_url")
            })

        return results
    except Exception as e:
        print(e, ": had trouble finding youtube link")
        return None



def download_audio(youtube_url: str, file_name: str, duration: int = 30) -> str:
    """
    Downloads audio from YouTube using yt-dlp and returns the local file path.
    Works on Windows.
    """
    try:
        os.makedirs(TEMP_DIR, exist_ok=True)

        # unique filename for Windows safe paths
        output_path = os.path.join(TEMP_DIR, file_name + ".wav")

        if os.path.exists(os.path.join(TEMP_DIR, file_name + ".wav")):
            return output_path

        ydl_opts = {
            "format": "bestaudio/best",       # best audio only
            "quiet": True,                    # suppress verbose logs
            "cookiefile": "cookies.txt",
            "outtmpl": os.path.join(TEMP_DIR, f"{file_name}.%(ext)s"),# temp file (converted later)
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",      # output wav
                "preferredquality": "192",    # doesn’t matter much, we’ll resample anyway
            }],
            "postprocessor_args": [
                "-t", str(duration),          # trim to N seconds
                "-ar", "16000",               # resample to 16kHz
                "-ac", "1"                    # mono
            ]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

        temp_file = os.path.join(TEMP_DIR, "temp.wav")
        if os.path.exists(temp_file):
            os.rename(temp_file, output_path)

        return output_path

    except Exception as e:
        print(e, ": had trouble downloading youtube link")
        return None


def embed(audio_file: str) -> str:
    try:
        audio, sr = sf.read(audio_file)
        emb, ts = openl3.get_audio_embedding(
            audio, sr,
            content_type="music",   # "music" or "env"
            input_repr="mel256",    # recommended
            embedding_size=512      # 512D vectors
        )
        # Pool over time axis → single vector per track
        return emb.mean(axis=0)

    except Exception as e:
        print(e, ": had trouble embedding")


def track_to_embeddings(artist: str, title: str, duration=60):
    try:
        query = f"{artist} {title}"
        url = search_youtube_yt_dlp(query)
        print(url)

        path_to_file = download_audio(url[0]['url'], f"{artist}_{title}")

        emb = embed(path_to_file)

        file_path = Path(path_to_file)

        if file_path.exists():
            file_path.unlink()
            print("Deleted.")

        return emb.tolist()  # convert numpy → JSON serializable
    except Exception as e:
        print(e, ": could not embed")
        
        return None
