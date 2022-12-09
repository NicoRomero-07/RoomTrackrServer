from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List, Optional, Union
from app.model import User

router = APIRouter()

'''CREATE USER'''
@router.post("/", response_description="Create a new user", status_code=status.HTTP_201_CREATED, response_model=User)
def create_user(request: Request, user: User = Body(...)):
    user = jsonable_encoder(user)
    new_user = request.app.database["user"].insert_one(user)
    created_user = request.app.database["user"].find_one(
        {"_id": new_user.inserted_id}
    )
    return created_user