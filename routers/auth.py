

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from store.database import db_session
from utils import services
from datetime import timedelta
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from schemas import users_schema
from starlette.responses import RedirectResponse
from starlette import status


routers = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
templates = Jinja2Templates(directory='templates')

#User Registration Routes
@routers.post("/token")
async def login_for_access_token(response:Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db:db_session):

    token = services.authenticate_user(form_data.username, form_data.password, timedelta(minutes=60), db)
    if token == False:
        return False
    response.set_cookie(key = "access_token", value=token, httponly=True)
    return True

@routers.get("/login", response_class=HTMLResponse)
async def login(request:Request):
    return templates.TemplateResponse('login.html', {'request': request})

@routers.post("/login", response_class=HTMLResponse)
async def login(request:Request,
    db:db_session):

    msg = []


    try:
        form=users_schema.LoginForm(request)
        await form.create_auth_form()
        response=RedirectResponse("/webpage/dashboard", status_code=status.HTTP_302_FOUND)
        validate_user_cookie=await login_for_access_token(response= response, form_data=form, db=db)

        if not validate_user_cookie:
            msg.append('Invalid Login Credential')
            return templates.TemplateResponse('login.html', {'request':request, 'msg':msg})    
        
        return response
    
    except HTTPException:
        msg.append('Unknown Error')

        return templates.TemplateResponse('login.html', {'request':request, 'msg':msg})