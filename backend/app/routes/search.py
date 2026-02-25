from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.models import Song
from app.utils.dependencies import get_db

from pydantic import BaseModel

router = APIRouter()

class SongSearchRequest(BaseModel):
    artist: str
    title: str

@router.post("/search")
def search_songs(request: SongSearchRequest, db: Session = Depends(get_db)):
    """
    Search for similar songs based on artist and title.
    Returns top 5 most similar songs using vector similarity.
    """
    try:
        artist = request.artist.strip()
        title = request.title.strip()

        # Validate input
        if not artist or not title:
            raise HTTPException(status_code=400, detail="Artist and title are required")

        # Find the query song
        song = db.query(Song).filter(
            Song.title == title,
            Song.artist == artist
        ).first()

        if song is None:
            raise HTTPException(
                status_code=404,
                detail=f"Song '{title}' by '{artist}' not found in database"
            )

        # Check if embedding exists
        if song.embedding is None:
            raise HTTPException(
                status_code=500,
                detail="Song found but embedding is missing"
            )

        # Find similar songs using vector similarity
        top_songs = (
            db.query(Song)
            .order_by(Song.embedding.l2_distance(song.embedding))
            .limit(6)  # Get 6 (first will be the query song itself)
            .all()
        )

        # Exclude the query song from results
        similar_songs = [
            {"id": r.id, "title": r.title, "artist": r.artist}
            for r in top_songs[1:]
        ]

        return {
            "status": "success",
            "query": {"title": title, "artist": artist},
            "songs": similar_songs
        }

    except HTTPException:
        raise
    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Error in search endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while searching for similar songs"
        )