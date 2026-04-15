from fastapi import APIRouter, Depends, HTTPException,Request
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.hotel import Hotel
from app.core.dependencies import get_current_user,require_permission
from app.core.hotel_enums import StateEnum, CountryEnum
from pydantic import BaseModel
from typing import Optional
from app.core.rate_limiter import fixed_window_rate_limit,sliding_window_rate_limiter

from app.schemas.schemas import HotelUpdate
from pydantic import BaseModel
from app.schemas.schemas import CreateHotel
from typing import Annotated
from app.models.user import User

SessionDep = Annotated[Session, Depends(get_db)]
CurretUser = Annotated[User,Depends(get_current_user)]


router = APIRouter()




@router.post("/")
def create_hotel(
    # name: str,
    # address: str,
    # city: str,
    # state: StateEnum,
    # country: CountryEnum,
    data : CreateHotel,
    db: SessionDep,
    current_user:CurretUser,
    # user = Depends(require_permission("add_hotel"))   #permission endpoint

):
    name = data.name
    address = data.address
    city= data.city
    state = data.state
    country = data.country
    
    hotel = Hotel(
        name=name,
        address=address,
        city=city,
        state=state,
        country=country,
        owner_id=current_user.id
    )
    db.add(hotel)
    db.commit()
    db.refresh(hotel)
    return hotel

@router.get("/")
def get_all_hotels(request:Request,db: SessionDep,current_user:CurretUser):
    
    client_host = request.client.host
    
    # fixed_window_rate_limit(current_user.id,"create_booking")
    sliding_window_rate_limiter(client_host,"get_all_hotels")
    
    hotels = db.query(Hotel).all()
    return hotels

@router.get("/my")
def get_my_hotels(
    db: SessionDep,
    current_user:CurretUser
):
    hotels = db.query(Hotel).filter(
        Hotel.owner_id == current_user.id
    ).all()
    return hotels

@router.get("/{hotel_id}")
def get_hotel(hotel_id: int, db: SessionDep):
    hotel = db.query(Hotel).filter(
        Hotel.hotel_id == hotel_id
    ).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return hotel



@router.patch("/{hotel_id}")
def update_hotel(
    hotel_id: int,
    hotel_update: HotelUpdate,
    db: SessionDep,
    current_user:CurretUser
):
    hotel = db.query(Hotel).filter(
        Hotel.hotel_id == hotel_id,
        Hotel.owner_id == current_user.id 
    ).first()

    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found or user not authorized to update")

 
    for field, value in hotel_update.model_dump(exclude_unset=True).items():
        setattr(hotel, field, value)

    db.commit()
    db.refresh(hotel)
    return hotel

@router.delete("/{hotel_id}")
def delete_hotel(
    hotel_id: int,
    db: SessionDep,
    current_user:CurretUser
):
    hotel = db.query(Hotel).filter(
        Hotel.hotel_id == hotel_id,
        Hotel.owner_id == current_user.id # Ensure the user owns the hotel
    ).first()

    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found or user not authorized to delete")

    db.delete(hotel)
    db.commit()
    return {"detail": "Hotel deleted successfully"}


