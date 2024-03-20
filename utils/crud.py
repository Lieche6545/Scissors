"""CRUD operations."""

from config.config import get_settings
from starlette.datastructures import URL
from schemas import url
from utils import keygen, qrcode
from store import models
from sqlalchemy.orm import Session
from datetime import datetime


base_url = URL(get_settings().base_url)



def create_and_save_url(db, title, url, user_id) -> url.URL:
    
    """Create URL in the Database."""
    #generate unique key
    key = keygen.create_unique_random_key(db)

    #database dump
    db_url = models.URL(
        title = title,
        destination= url,
        key= key,
        date_created = datetime.now().date(), 
        owner_id = user_id
    )
    db.add(db_url)
    db.commit()
    return db_url

#function 2
def get_url_by_key(url_key:str, db:Session) -> models.URL:
    """Return a URL by specified key."""
    
    return (
        db.query(models.URL)
        .filter(models.URL.key == url_key)
        .first()
    )


def update_db_clicks(db: Session, db_url: models.URL) -> models.URL:
    """Update the count of times the link has been visited."""
    db_url.clicks += 1
    db.commit()
    db.refresh(db_url)
    return db_url    
