

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from models.room import Room
from models.hotel import Hotel
from core.dependencies import get_current_user

router = APIRouter()


@router.post("/")
def create_room(
    hotel_id: int,
    room_type: str,
    total_rooms: int,
    price: float,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    hotel = db.query(Hotel).filter(Hotel.hotel_id == hotel_id).first()

    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    room = Room(
        hotel_id=hotel_id,
        room_type=room_type,
        total_rooms=total_rooms,
        price=price
    )

    db.add(room)
    db.commit()
    db.refresh(room)

    return room


@router.get("/hotel/{hotel_id}")
def get_rooms_by_hotel(hotel_id: int, db: Session = Depends(get_db)):

    rooms = db.query(Room).filter(Room.hotel_id == hotel_id).all()

    return rooms


@router.patch("/{room_id}")
def update_room(
    room_id: int,
    price: float,
    db: Session = Depends(get_db)
):

    room = db.query(Room).filter(Room.room_id == room_id).first()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    room.price = price

    db.commit()
    db.refresh(room)

    return room


@router.delete("/{room_id}")
def delete_room(room_id: int, db: Session = Depends(get_db)):

    room = db.query(Room).filter(Room.room_id == room_id).first()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    db.delete(room)
    db.commit()

    return {"message": "Room deleted"}
