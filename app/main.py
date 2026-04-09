from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse

from app import crud
from app.db import get_db, Base, engine
from app.schemas import URL_from_client, URL_response, URL_response_statistics

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="URL Shortener API",
    description="A simple URL shortener service built with FastAPI and SQLAlchemy",
    version="1.0.0",
)


@app.post("/shorten", response_model=URL_response, status_code=201)
def create_short_url(url_data: URL_from_client, db: Session = Depends(get_db)):
    original_url = str(url_data.url)
    new_url = crud.create_short_url(db, original_url)
    return URL_response(
        id=new_url.id,
        original_url=new_url.original_url,
        short_id=new_url.short_id,
        clicks=new_url.clicks,
        created_at=new_url.created_at
    )


@app.get('/stats/{short_id}', response_model=URL_response_statistics)
def get_url_statistics(short_id: str, db: Session = Depends(get_db)):
    url = crud.get_short_url(db, short_id)
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    return URL_response_statistics(
        short_id=url.short_id,
        total_clicks=url.clicks,
        created_at=url.created_at
    )


@app.get('/{short_id}')
def redirect_to_original_url(short_id: str, db: Session = Depends(get_db)):
    url = crud.get_short_url(db, short_id)
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    crud.increment_clicks(db, url)
    return RedirectResponse(url=url.original_url, status_code=302)