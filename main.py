from fastapi import FastAPI
from routers import auth, url, users
from store.models import Base
from store.database import engine
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

app = FastAPI(
    openapi_tags=[{
        "name": "auth",
        "description": "Authentication related routes",
    },
    {
        "name": "users",
        "description": "Authentication related routes",
    },
    {
        "name": "links",
        "description": "Authentication related routes",
    }],
    title="Li'eche Scissor App",
    description= "A FastAPI-based URL shortener and redirector.",
    version="0.1.0", 
)


Base.metadata.create_all(bind=engine) # Command to cretae the database

app.include_router(auth.routers)
app.include_router(users.routers)
app.include_router(url.routers)
app.include_router(webpage.routers)

templates=Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    return {"Welcome to Scissors"}