from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from models.hotel import Hotel
from models.user import User
from core.dependencies import get_current_user, require_permission
from typing import List
from schemas.schemas import HotelResponse

router = APIRouter()





router = APIRouter()

@router.get("/", response_model=List[HotelResponse])
def get_hotels(db: Session = Depends(get_db)):
    hotels = db.query(Hotel).all()
    if not hotels:
        raise HTTPException(status_code=404, detail="No hotels found")
    return hotels




from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_hotel(
    name: str, 
    address: str, 
    city: str, 
    state: str, 
    country: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    try:
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

    except SQLAlchemyError as e:
        db.rollback()  
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the hotel."
        )





@router.get("/{hotel_id}")
def get_hotel(hotel_id: int, db: Session = Depends(get_db)):

    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()

    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    return hotel



#update hotel

@router.patch("/{hotel_id}")
def update_hotel(
    hotel_id: int,
    name: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()

    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    if hotel.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    hotel.name = name

    db.commit()
    db.refresh(hotel)

    return hotel


#delete hotel

@router.delete("/{hotel_id}")
def delete_hotel(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()

    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    if hotel.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    db.delete(hotel)
    db.commit()

    return {"message": "Hotel deleted"}