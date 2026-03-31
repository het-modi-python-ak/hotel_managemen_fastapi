
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from models.hotel import Hotel
from core.dependencies import get_current_user
from core.hotel_enums import StateEnum,CountryEnum

router = APIRouter()


@router.post("/")
def create_hotel(
    name: str,
    address: str,
    city: str,
    state: StateEnum,
    country: CountryEnum,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
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