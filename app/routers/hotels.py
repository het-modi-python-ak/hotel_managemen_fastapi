from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from models.hotel import Hotel
from core.dependencies import get_current_user,require_permission
from core.hotel_enums import StateEnum, CountryEnum
from pydantic import BaseModel
from typing import Optional


class HotelUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[StateEnum] = None
    country: Optional[CountryEnum] = None

router = APIRouter()

@router.post("/")
def create_hotel(
    name: str,
    address: str,
    city: str,
    state: StateEnum,
    country: CountryEnum,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    user = Depends(require_permission("add_hotel"))   #permission endpoint

):
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
def get_all_hotels(db: Session = Depends(get_db)):
    hotels = db.query(Hotel).all()
    return hotels

@router.get("/my")
def get_my_hotels(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    hotels = db.query(Hotel).filter(
        Hotel.owner_id == current_user.id
    ).all()
    return hotels

@router.get("/{hotel_id}")
def get_hotel(hotel_id: int, db: Session = Depends(get_db)):
    hotel = db.query(Hotel).filter(
        Hotel.hotel_id == hotel_id
    ).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return hotel

# --- New Endpoints ---

@router.put("/{hotel_id}")
def update_hotel(
    hotel_id: int,
    hotel_update: HotelUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    hotel = db.query(Hotel).filter(
        Hotel.hotel_id == hotel_id,
        Hotel.owner_id == current_user.id # Ensure the user owns the hotel
    ).first()

    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found or user not authorized to update")

    # Update attributes dynamically based on the Pydantic model
    for field, value in hotel_update.dict(exclude_unset=True).items():
        setattr(hotel, field, value)

    db.commit()
    db.refresh(hotel)
    return hotel

@router.delete("/{hotel_id}")
def delete_hotel(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
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
