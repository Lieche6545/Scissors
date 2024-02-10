from fastapi import APIRouter
from schemas.users_schema import User

users_router = APIRouter()

users = [
    User(),
    User()
]
    

