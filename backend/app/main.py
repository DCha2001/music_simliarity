from fastapi import FastAPI
from app.routes import search
from app.db.db import init_db

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",  # React/Next.js dev server
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Allowed origins
    allow_credentials=True,
    allow_methods=["*"],              # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],              # Custom headers
)

app.include_router(search.router, prefix="/api", tags=["Search"])

init_db()

@app.get("/api/hello")
async def hello():
    return {"message": "Hello from FastAPI!"}

