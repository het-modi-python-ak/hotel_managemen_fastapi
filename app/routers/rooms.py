from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from models.room import Room
from models.hotel import Hotel
from core.dependencies import get_current_user

router = APIRouter()


@router.post("/")
def add_room(
    hotel_id: int,
    room_number: str,
    room_type: str,
    price: float,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()

    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    if hotel.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    room = Room(
        hotel_id=hotel_id,
        room_number=room_number,
        room_type=room_type,
        price=price
    )

    db.add(room)
    db.commit()
    db.refresh(room)

    return room


#get rooms
@router.get("/{hotel_id}")
def get_rooms(hotel_id: int, db: Session = Depends(get_db)):

    rooms = db.query(Room).filter(Room.hotel_id == hotel_id).all()

    if not rooms:
        raise HTTPException(status_code=404, detail="No rooms found")

    return rooms

