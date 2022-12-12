from email.headerregistry import Address
from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from app.model import Address, AddressUpdate
from typing import List
from typing import Optional

router = APIRouter()

'''LIST ADDRESSES'''
@router.get("/",response_description="List all addresses", response_model=List[Address])
def list_addresses(request: Request):
    addresses = list(request.app.database["address"].find(limit=100))
    return addresses

'''CREATE ADDRESS'''
@router.post("/", response_description="Create a new address", status_code=status.HTTP_201_CREATED, response_model=Address)
def create_address(request: Request, address: Address = Body(...)):

    address = jsonable_encoder(address)
    new_address = request.app.database["address"].insert_one(address)
    created_address = request.app.database["address"].find_one(
        {"_id": new_address.inserted_id}
    )

    return created_address

'''GET ADDRESS'''
@router.get("/{id}", response_description="Get a single address", response_model=Address)
def get_address(id:str, request: Request):
    if(address := request.app.database["address"].find_one({"id": id})) is not None:
        return address

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Address with ID {id} not found")

'''UPDATE ADDRESS'''
@router.put("/{id}", response_description="Update a address", response_model=Address)
def update_address(id:str, request: Request, data: AddressUpdate = Body(...)):

    address = {k: v for k, v in data.dict().items() if v is not None}
    
    if len(address) >= 1:
        update_result = request.app.database["address"].update_one(
            {"id": id}, {"$set": address}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Address with ID {id} not found")

    if (
        existing_address:= request.app.database["address"].find_one({"id":id})
    ) is not None:
        return existing_address

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Address with ID {id} not found")

'''DELETE ALL ADDRESSES'''
@router.delete("/delete_all", response_description="Delete all addresses")
def delete_all_addresses(request: Request, response: Response):
    address_deleted = request.app.database["address"].delete_many({})

    if address_deleted.deleted_count:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Address not found")

'''DELETE ADDRESS'''
@router.delete("/{id}", response_description="Delete a address")
def delete_address(id:str, request: Request, response: Response):
    address_deleted = request.app.database["address"].delete_one({"id": id})

    if address_deleted.deleted_count:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Address with ID {id} not found")
