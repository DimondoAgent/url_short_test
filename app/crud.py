#created this file to remove all these operations from API endpoints and keep them in one place,
# which makes the code cleaner and more maintainable
from sqlalchemy.orm import Session

from app.models import URL
from app.utils import generate_short_string
from app.config import settings

def create_short_url(db: Session, original_url: str) -> URL:

    for _ in range(5):  # Try up to 5 times to generate a unique short string
        short_id = generate_short_string(settings.short_id_length)
        if not db.query(URL).filter(URL.short_id == short_id).first():
            break
    else:
        raise Exception("Failed to generate a unique short code after 5 attempts")
    
    new_url = URL(original_url=original_url, short_id=short_id)
    db.add(new_url)
    db.commit()
    db.refresh(new_url)
    return new_url

def get_url_by_short_id(db: Session, short_id: str) -> URL:
    return db.query(URL).filter(URL.short_id == short_id).first()

def increment_clicks(db: Session, url: URL) -> None:
    url.clicks += 1
    db.commit() 
    db.refresh(url)
    return url

