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


# Customize URL USer Information By USer ONly
@routers.put("/custom/{url_key}")
async def customize_url(url_key: str, custom_url: str, db:Session=Depends(database.get_db), token:str=Depends(oauth2_scheme)):

    # Authentication
    user = services.get_user_from_token(db, token)

    # Authorization
    scan_user = db.query(models.USER).filter(models.USER.email == user.email)
    if not scan_user.first():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized User"
        )
    
    scan_key = db.query(models.URL).filter(models.URL.key == url_key, models.URL.is_active == True)

    if crud.get_url_by_key(custom_url, db) == True:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Already Taken"
        )
    
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
        
# # Generate QRCode Route
# @routers.put("/drcode/{url_key}")
# async def add_qrcode_to_url(url_key: str, db:Session=Depends(database.get_db), token: str=Depends(oauth2_scheme)):
#         # Generate QRcode for website, for registered users only

#     # Authentication
#     user = service.get_url_from_token(db, token)

#     db_url = crud.get_url_by_key(url_key, db)
#     if not db_url:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail= f"No MAtch Found For {url_key} Key"
#         )
#     if db_url.owner_id != user.id:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail= "Owners Permission Required"
#         )
    
#     if not db_url:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail= "URL Key Not Found"
#         )
#     qr = crud.make_qrcode(url_key = db_url.key)
#     save_qr = db.query(models.URL).filter(models.URL.key == url_key)
#     if save_qr.first():
#         save_qr.update({"qr_url": qr})
#         db.commit()

#     return FileResponse(qr, media_type="image/png")

# # Download QR-Code Route
# @routers.get("/download/{url_key}")
# async def download_qr(url_key:str, db:Session=Depends(database.get_db)):

#     db_url = crud.get_url_by_key(url_key, db)

#     if not db_url:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail= "QR Code Key Not Found")
#     return FileResponse(
#         filename=db_url.key,
#         path=db_url.qr_url,
#         media_type="image/png",
#         content_disposition_type= "attachment"
#     )
    
