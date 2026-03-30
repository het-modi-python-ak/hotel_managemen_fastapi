from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from models.room import Room
from models.hotel import Hotel
from models.room_type import RoomType
from core.dependencies import get_current_user

router = APIRouter()


@router.post("/")
def create_room(
    hotel_id: int,
    room_type: RoomType,
    price: float,
    total_rooms: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    hotel = db.query(Hotel).filter(
        Hotel.hotel_id == hotel_id
    ).first()

    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    if hotel.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    room = Room(
        hotel_id=hotel_id,
        room_type=room_type,
        price=price,
        total_rooms=total_rooms
    )

    db.add(room)
    db.commit()
    db.refresh(room)

    return room


@router.get("/{hotel_id}")
def get_rooms(hotel_id: int, db: Session = Depends(get_db)):

    rooms = db.query(Room).filter(
        Room.hotel_id == hotel_id
    ).all()

    return rooms