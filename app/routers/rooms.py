from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.room import Room
from app.models.hotel import Hotel
from app.models.room_type import RoomType 
from app.core.dependencies import get_current_user
from typing import Optional
router = APIRouter()

@router.post("/{hotel_id}", status_code=status.HTTP_201_CREATED)
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
    
    if price < 1:
        raise HTTPException(status_code=422, detail="price should be greater then 0")
    
    if hotel_id<1:
        raise HTTPException(status_code=422, detail= "hotel id can not be less than 1")
    
    if total_rooms < 1:
        raise HTTPException(status_code=422, detail="total rooms can not be less than 0")
    


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

@router.patch("/{hotel_id}/{room_id}")
def update_room(
    hotel_id: int,
    room_id: int,
    price: Optional[float] = None,
    total_rooms: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    #  Check if the hotel exists and belongs to the user
    hotel = db.query(Hotel).filter(
        Hotel.hotel_id == hotel_id,
        Hotel.owner_id == current_user.id
    ).first()

    if not hotel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Hotel not found or user not authorized"
        )

    # Check if the room exists and belongs to this specific hotel
    room = db.query(Room).filter(
        Room.room_id == room_id,
        Room.hotel_id == hotel_id
    ).first()

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Room not found in this hotel"
        )

   
    if price is not None:
        if price < 1:
            raise HTTPException(status_code=422, detail="Price should be greater than 0")
        room.price = price
        
    if total_rooms is not None:
        if total_rooms < 0:
            raise HTTPException(status_code=422, detail="Total rooms cannot be negative")
        room.total_rooms = total_rooms

    db.commit()
    db.refresh(room)

    return room

@router.delete("/{hotel_id}/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(
    hotel_id:int,
    room_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    hotel = db.query(Room).filter(Room.hotel_id==hotel_id).all()
    
    if not hotel:
        raise HTTPException(status_code=404, detail="No rooms exists in the hotel")
    
    room = db.query(Room).filter(Room.room_id == room_id,Room.hotel_id==hotel_id).first()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Check if the user owns the hotel associated with the room
    hotel = db.query(Hotel).filter(Hotel.hotel_id == room.hotel_id).first()
    if hotel.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    db.delete(room)
    db.commit()
    
    return {"message": "Room deleted successfully"}
