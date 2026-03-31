from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from models.room import Room
from models.hotel import Hotel
# Assuming RoomType is an Enum or similar defined in models.room_type
from models.room_type import RoomType 
from core.dependencies import get_current_user
# Assuming a Pydantic model for updating rooms, like a RoomUpdate schema
# from schemas.room import RoomUpdate 

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
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

@router.put("/{room_id}")
def update_room(
    room_id: int,
    # Use a Pydantic schema here for better validation of incoming data
    # update_data: RoomUpdate, 
    # For simplicity, using individual parameters as in the original code:
    price: float = None,
    total_rooms: int = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    room = db.query(Room).filter(Room.room_id == room_id).first()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Check if the user owns the hotel associated with the room
    hotel = db.query(Hotel).filter(Hotel.hotel_id == room.hotel_id).first()
    if hotel.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    # Update attributes if provided
    if price is not None:
        room.price = price
    if total_rooms is not None:
        room.total_rooms = total_rooms
    
    db.commit()
    db.refresh(room)

    return room

@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    room = db.query(Room).filter(Room.room_id == room_id).first()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Check if the user owns the hotel associated with the room
    hotel = db.query(Hotel).filter(Hotel.hotel_id == room.hotel_id).first()
    if hotel.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    db.delete(room)
    db.commit()
    
    return {"message": "Room deleted successfully"}
