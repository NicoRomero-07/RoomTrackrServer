from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List
from app.model import Booking,BookingUpdate
from datetime import datetime 
from app.routers import household_router

router = APIRouter()

'''LIST BOOKINGS'''
@router.get("/",response_description="List all bookings", response_model=List[Booking])
def list_bookings(request: Request):
    bookings = list(request.app.database["booking"].find(limit=100))
    return bookings

'''GET BOOKING'''
@router.get("/{id}", response_description="Get a single booking", response_model=Booking)
def get_booking(id:str, request: Request):
    if(booking := request.app.database["booking"].find_one({"id":id})):
        return booking

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Booking with ID {id} not found")

'''CREATE BOOKING'''
@router.post("/", response_description="Create a new book", status_code=status.HTTP_201_CREATED, response_model=Booking)
def create_household(request: Request, Booking: Booking = Body(...)):

    Booking = jsonable_encoder(Booking)
    
    household = household_router.get_household(Booking.get('household').get('id'), request)
    Booking['household']['title'] = household.get('title')
    Booking['household']['address']['street'] = household.get('address').get('street')
    Booking['household']['address']['number'] = household.get('address').get('number')
    Booking['household']['photo'] = household.get('photo')[0]
    #Booking['household']['address']['postal_code'] = household.get('address').get('postal_code')
    
    #Get and set host and renter data
    
    
    new_booking= request.app.database["booking"].insert_one(Booking)
    created_booking = request.app.database["booking"].find_one(
        {"_id": new_booking.inserted_id}
    )

    format_data = '%Y-%m-%dT%H:%M:%S.%f'
    try:
        startDate = datetime.strptime(Booking.get('start'),format_data)
    except ValueError:
        print('Start datetime format not valid')

    try:
        endingDate = datetime.strptime(Booking.get('ending'),format_data)
    except ValueError:
        print('Ending datetime format not valid')
        
    if startDate < datetime.now():
        raise ValueError("Start date must be in the future")
    if endingDate < datetime.now():
        raise ValueError("Ending date must be in the future")
    
    
    
    
    return created_booking


'''UPDATE BOOKING '''
@router.put("/{id}", response_description="Update a book", response_model=Booking)
def update_book(id: str, request: Request, booking: BookingUpdate = Body(...)):
    booking = {k: v for k, v in booking.dict().items() if v is not None}

    if len(booking) >= 1:
        update_result = request.app.database["booking"].update_one(
            {"id": id}, {"$set": booking}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {id} not found")

    if (
        existing_book := request.app.database["booking"].find_one({"id":id})
    ) is not None:
        return existing_book

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {id} not found")

'''DELETE ALL BOOKINGS'''
@router.delete("/delete_all", response_description="Delete all bookings")
def delete_all_household(request: Request, response: Response):
    household_deleted = request.app.database["booking"].delete_many({})

    if household_deleted.deleted_count:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Booking not found")

'''DELETE BOOKING'''
@router.delete("/{id}", response_description="Delete a booking")
def delete_booking(id:str,request: Request, response: Response):
    booking_deleted = request.app.database["booking"].delete_one({"id": id})

    if booking_deleted.deleted_count:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Booking with ID {id} not found")


'''LIST ACTIVE BOOKINGS (no relational)'''
@router.get("_actives",response_description="List all active bookings", response_model=List[Booking])
def list_active_bookings(request: Request):
    active_bookings = list(request.app.database["booking"].find({
    "ending": {
        "$gte": str(datetime.now())
    }},limit=100).sort("start", -1))
    return active_bookings

'''LIST INACTIVE BOOKINGS (no relational)'''
@router.get("_inactives",response_description="List all active bookings", response_model=List[Booking])
def list_incative_bookings(request: Request):
    active_bookings = list(request.app.database["booking"].find({
    "ending": {
        "$lte": str(datetime.now())
    }},limit=100).sort("start", -1))
    return active_bookings

'''GET BOOKINGS OF AN USER ORDER BY DATE (relational)'''
@router.get("/from_user/{username}", response_description="Get the bookings of an user ordered by date")
def get_ordered_bookings_by_username(username: str, request: Request, response: Response):

    bookings = list(request.app.database["booking"].find({"renter.renter_username": username},{'_id':0},limit = 100).sort("start", -1))
    return bookings

'''GET BOOKINGS OF A HOUSEHOLD ORDER BY DATE (relational)'''
@router.get("/from_household/{household_id}", response_description="Get the bookings of a household ordered by date")
def get_ordered_bookings_by_household_id(household_id: str, request: Request, response: Response):

    bookings = list(request.app.database["booking"].find({"household.id": household_id},{'_id':0},limit = 100).sort("start", -1))
    return bookings