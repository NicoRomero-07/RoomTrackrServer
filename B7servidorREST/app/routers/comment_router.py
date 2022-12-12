from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List
from typing import Optional
from app.model import User, Address, Comment, CommentUpdate, Household
import requests

router = APIRouter()


'''CREATE COMMENT'''


@router.post("/", response_description="Create a new comment", status_code=status.HTTP_201_CREATED, response_model=Comment)
def create_comment(request: Request, comment: Comment = Body(...)):

    comment = jsonable_encoder(comment)
        
    if request.app.database["household"].find_one({"id" : comment["household"]["id"]}) is None:
        raise HTTPException(status_code=404, detail="Household not found")
    
    if request.app.database["user"].find_one({"username" : comment["user"]["renter_username"]}) is None:
        raise HTTPException(status_code=404, detail="user not found")
    
    #Comprobar que el nombre de usuario coincide con el email de ese usuario
    
    new_comment = request.app.database["comment"].insert_one(comment)
    created_comment = request.app.database["comment"].find_one(
        {"_id": new_comment.inserted_id}
    )

    return created_comment


'''LIST COMMENTS'''


@router.get("/", response_description="List all comments", response_model=List[Comment])
def list_comments(request: Request):
    comments = list(request.app.database["comment"].find(limit=100))
    return comments


@router.get("/{id}", response_description="Get a single comment", response_model=Comment)
def get_comment(id: str, request: Request):
    if (comment := request.app.database["comment"].find_one({"id": id})) is not None:
        return comment

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Comment with ID {id} not found")


'''DELETE ALL COMMENTS'''


@router.delete("/delete_all", response_description="Delete all households")
def delete_all_comments(request: Request, response: Response):
    comment_deleted = request.app.database["comment"].delete_many({})

    if comment_deleted.deleted_count:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Comment not found")


'''DELETE COMMENT'''
@router.delete("/{id}", response_description="Delete a comment")
def delete_comment(id: str, request: Request, response: Response):
    comment_deleted = request.app.database["comment"].delete_one({"id": id})

    if comment_deleted.deleted_count:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Comment with ID {id} not found")


'''UPDATE COMMENT'''


@router.put("/{id}", response_description="Update a comment", response_model=Comment)
def update_comment(id: str, request: Request, data: CommentUpdate = Body(...)):

    comment = {k: v for k, v in data.dict().items() if v is not None}

    if len(comment) >= 1:
        update_result = request.app.database["comment"].update_one(
            {"id": id}, {"$set": comment}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Comment with ID {id} not found")

    if (
        existing_household := request.app.database["comment"].find_one({"id": id})
    ) is not None:
        return existing_household

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Comment with ID {id} not found")

