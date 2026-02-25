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
    try:
        artist = request.artist
        title = request.title

        song = db.query(Song).filter(Song.title == title, Song.artist == artist).all()
        print(song)

        if song is None or len(song) == 0:
            raise HTTPException(status_code=404, detail="Song not found")
        

        top_songs = (
                            db.query(Song)
                            .order_by(Song.embedding.l2_distance(song[0].embedding))
                            .limit(6)
                            .all()
                        )
        

        songs = [
            {"id": r.id, "title": r.title, "artist": r.artist}
            for r in top_songs[1:]
        ]

        return {"status": "success", "songs": songs}
    except Exception as e:
        return {"status": "error", "message": str(e.detail) if isinstance(e, HTTPException) else str(e) }