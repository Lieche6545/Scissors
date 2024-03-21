import validators
from fastapi import APIRouter, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse
from schemas import url
from sqlalchemy.orm import Session
from store import database, models
from utils import crud, services
from routers.auth import oauth2_scheme
from starlette.datastructures import URL
from config.config import get_settings
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates




routers = APIRouter(tags=["links"])

templates = Jinja2Templates(directory= "templates")

# Viewing URL By Key
@routers.get("/", response_class= HTMLResponse)
async def index_page(
    request:Request
):
    
    return templates.TemplateResponse("index.html", {"request": request})

# Create URL Route
@routers.get("/create_url", response_class=HTMLResponse)
async def create_url(request: Request):
    return templates.TemplateResponse("create_url.html", {"request": request})

@routers.post("/create_url", response_class=HTMLResponse)
# @rate_limited(max_calls=3, time_frame=60)
async def create_url(
    request: Request,
    target_url: str = Form(...),
    title: str = Form(...),
    db:Session=Depends(database.get_db)
):
    
    
    """Create a URL shortener entry."""
    
    msg = []
    
    # authentication
    user = services.get_user_from_token(request, db)
    
    if not user:
        msg.append("Session Expired, Login")
        return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
    
    if not validators.url(target_url):
        msg.append("Invalid destination url, kindly include: https:// or http://")
        return templates.TemplateResponse("create_url.html", 
            {
                "request": request,
                "msg": msg, 
                "user": user, 
                "target_url": target_url,
                "title": title
            }
        )
    
    db_url = crud.create_and_save_url(
        db=db, 
        title=title, 
        url=target_url, 
        user_id = user.id
    )
    db.refresh(db_url)
    return RedirectResponse("/webpage/dashboard", status_code=status.HTTP_302_FOUND)


# Customize URL User Information By User Only
@routers.get("/edit_url/{url_key}", response_class=HTMLResponse)
async def edit_url(request: Request, url_key: str, db:Session=Depends(database.get_db)):

    msg = []

    # Authentication
    user = services.get_user_from_token(request, db)

    # Authorization
    if not user:
        msg.append("Session expired, kindly login")
        return templates.TemplateResponse("login.html", 
            {
                "request": Request,
                "msg": msg, 
            }
        )
        
    scan_key = db.query(models.URL).filter(models.URL.key == url_key).first()
    return templates.TemplateResponse(
        "customise_url.html", 
            {
                "request": request,
                "msg": msg,
                "user": user,
                "scan_key": scan_key
            }
        )
    
@routers.post("/edit_url/{url_key}")
async def edit_url(
    request: Request, 
    url_key: str, 
    db:Session=Depends(database.get_db),
    title: str=Form(...),
    destination: str=Form(...),
    custom_name: str=Form(...),
    ):

    msg = []

    # Authentication
    user = services.get_user_from_token(request, db)

    # Authorization
    if not user:
        msg.append("Session expired, kindly login")
        return templates.TemplateResponse("login.html", 
            {
                "request": Request,
                "msg": msg, 
            }
        )
    
    scan_key = db.query(models.URL).filter(models.URL.key == url_key).first()
    if not scan_key:
        return RedirectResponse("/webpage/dashboard", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    
    check = crud.get_url_by_key(url_key=custom_name, db=db)
    if check:
        msg.append("Name has been taken")
        return templates.TemplateResponse("customise_url.html", 
            {
                "request": Request,
                "msg": msg,
                "url_key": url_key
            }
        )
    
    scan_key.key= custom_name
    scan_key.title= title
    scan_key.destination= destination

    db.add(scan_key)
    db.commit()

    return RedirectResponse("/webpage/dashboard", status_code=status.HTTP_302_FOUND)



    
    # View URL By Key
@routers.get("/{url_key}")
async def redirect_url(
    url_key: str,
    db:Session=Depends(database.get_db)
):
        
    if db_url := crud.get_url_by_key(db=db, url_key=url_key):
        crud.update_db_clicks(db=db, db_url=db_url)
        return RedirectResponse(db_url.destination)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail= f"No Match Found For {url_key} Key"
        )
        
# Delete Entry Routes
@routers.get("/delete/{url_key}", response_class=HTMLResponse)
async def delete_url(
    request:Request, 
    url_key: str, 
    db:Session=Depends(database.get_db)
    ):
    
    msg = []
    
    user = services.get_user_from_token(request, db)
    if user is None:
        msg.append("session expired, kindly Login again")
        return templates.TemplateResponse(
            "login.html", 
            {'request':Request, 'msg':msg}, 
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    url_model = db.query(models.URL).filter(models.URL.key == url_key, models.URL.owner_id == user.id).first()
    if url_model is None:
        return RedirectResponse("/webpage/dashboard", status_code=status.HTTP_302_FOUND)
    
    db.delete(url_model)
    db.commit()
    return RedirectResponse("/webpage/dashboard", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
