from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession  # Changed
from sqlalchemy.future import select             # Added for async queries
from app.database.database import get_db
from app.models.room import Room
from app.models.hotel import Hotel
from app.core.dependencies import get_current_user
from typing import Annotated
from app.models.user import User
from app.schemas.schemas import CreateRoom, UpdateRoom


SessionDep = Annotated[AsyncSession, Depends(get_db)]
CurretUser = Annotated[User, Depends(get_current_user)]

router = APIRouter()


@router.post("/{hotel_id}", status_code=status.HTTP_201_CREATED)
async def create_room(  
    data: CreateRoom,
    db: SessionDep,
    current_user: CurretUser
):
    
    result = await db.execute(select(Hotel).filter(Hotel.hotel_id == data.hotel_id))
    hotel = result.scalars().first()

    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    if hotel.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    
    
    result = await db.execute(
        select(Room).filter(Room.hotel_id == data.hotel_id, Room.room_type == data.room_type)
    )
    existing_room = result.scalars().first()

    if existing_room:
        raise HTTPException(
            status_code=400, 
            detail=f"Room category '{data.room_type}' already exists for this hotel."
        )

    # 3. Create and Save
    room = Room(
        hotel_id=data.hotel_id,
        room_type=data.room_type,
        price=data.price,
        total_rooms=data.total_rooms
    )

    db.add(room)
    await db.commit()   # Added await
    await db.refresh(room) # Added await
    return room


@router.get("/{hotel_id}")
async def get_rooms(hotel_id: int, db: SessionDep):
    result = await db.execute(select(Room).filter(Room.hotel_id == hotel_id))
    rooms = result.scalars().all()
    return rooms


@router.patch("/{hotel_id}/{room_id}")
async def update_room(
    hotel_id: int,
    room_id: int, 
    db: SessionDep,
    current_user: CurretUser,
    data: UpdateRoom
):
    # Check hotel ownership
    result = await db.execute(
        select(Hotel).filter(Hotel.hotel_id == hotel_id, Hotel.owner_id == current_user.id)
    )
    hotel = result.scalars().first()

    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found or unauthorized")

    # Check room existence
    result = await db.execute(
        select(Room).filter(Room.room_id == room_id, Room.hotel_id == hotel_id)
    )
    room = result.scalars().first()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if data.price is not None:
        room.price = data.price
    if data.total_rooms is not None:
        room.total_rooms = data.total_rooms

    await db.commit()
    await db.refresh(room)
    return room


@router.delete("/{hotel_id}/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(
    hotel_id: int,
    room_id: int,
    db: SessionDep,
    current_user: CurretUser
):
    # 1. Get room and join with hotel to check ownership in one query
    result = await db.execute(
        select(Room).filter(Room.room_id == room_id, Room.hotel_id == hotel_id)
    )
    room = result.scalars().first()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # 2. Check ownership
    result = await db.execute(select(Hotel).filter(Hotel.hotel_id == room.hotel_id))
    hotel = result.scalars().first()
    
    if hotel.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    await db.delete(room)
    await db.commit()
    return None
