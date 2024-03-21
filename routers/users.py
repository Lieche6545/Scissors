from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form, status
from sqlalchemy.orm import Session
from schemas import users_schema
from routers.url import routers
from store import database
from store import models
from utils.services import bcrypt_context #get_user_from_token
from routers.auth import oauth2_scheme
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError


routers = APIRouter(prefix="/users", tags=["users"])
templates = Jinja2Templates(directory="templates")

#New User Creation
@routers.get("/sign-up", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# #New User Registration
@routers.post("/sign-up", response_class=HTMLResponse)
async def register(
    request: Request,
    email: str = Form(...),
    firstname: str = Form(...),
    lastname: str = Form(...),
    password: str = Form(...),
    verify_password: str = Form(...),
    db:Session=Depends(database.get_db)
):
    
    msg = []
    
    if password != verify_password:
        msg.append("Passwords do not match")
        return templates.TemplateResponse(
            "register.html", 
            {"request": request, 
             "msg": msg,
             "email": email,
             "firstname": firstname,
             "lastname": lastname,
             })
    if len(password) < 6:
        msg.append("Password should be > 6 characters")
        return templates.TemplateResponse("register.html", {
            "request": request,
            "msg": msg,
            "email": email,
            "firstname": firstname,
            "lastname": lastname,
        })
    
    
    
    new_user = models.USER(
        firstname = firstname,
        lastname = lastname,
        email = email,
        password = bcrypt_context.hash(password)
    )
        
    
    try:
          db.add(new_user)
          db.commit()
          db.refresh(new_user)
          msg.append("Registration successful")
          return templates.TemplateResponse(
              "login.html",
              {"request": request,
               "msg": msg,
        })
    
    except IntegrityError:
        msg.append("Email Already Taken")
        return templates.TemplateResponse("register.html", {
            "request": request,
            "msg": msg,
            "email": email,
            "firstname": firstname,
            "lastname": lastname
        })





# # Editing User Information NB: Only a User can access this function
# @routers.put("/edit_user")
# async def edit_username(username, db:Session=Depends(database.get_db), token:str=Depends(oauth2_scheme)):

#     # Authentication
#     user = get_user_from_token(db, token)

#     # Authorization
#     scan_db = db.query(models.USER).filter(models.USER.email == user.email)
#     if not scan_db.first():
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail= "Unauthorized User"
#         )
    
#     scan_db.update({models.USER.username:username})
#     db.commit()
#     raise HTTPException(
#         status_code=status.HTTP_202_ACCEPTED,
#         detail="Information updates successfully"
#     )


 

