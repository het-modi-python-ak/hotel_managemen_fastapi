from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.database import get_db
from app.models.hotel import Hotel
from app.core.dependencies import get_current_user, require_permission
from app.core.rate_limiter import sliding_window_rate_limiter 
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.schemas import HotelUpdate, CreateHotel
from typing import Annotated
from app.models.user import User


SessionDep = Annotated[AsyncSession, Depends(get_db)]
CurretUser = Annotated[User, Depends(get_current_user)]

router = APIRouter()

@router.post("/")
async def create_hotel(
    data: CreateHotel,
    db: SessionDep,
    current_user: CurretUser,

    user = Depends(require_permission("add_hotel"))
):
    try:
        hotel = Hotel(
            name=data.name,
            address=data.address,
            city=data.city,
            state=data.state,
            country=data.country,
            owner_id=current_user.id
        )
        db.add(hotel)
        await db.commit()
        await db.refresh(hotel)
        return hotel
    except SQLAlchemyError as e:
        await db.rollback() 
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/")
async def get_all_hotels(request: Request, db: SessionDep):
    client_host = request.client.host
    
    sliding_window_rate_limiter(client_host, "get_all_hotels")
    
    result = await db.execute(select(Hotel))
    hotels = result.scalars().all()
    return hotels

@router.get("/my")
async def get_my_hotels(db: SessionDep, current_user: CurretUser):
    result = await db.execute(
        select(Hotel).filter(Hotel.owner_id == current_user.id)
    )
    return result.scalars().all()

@router.get("/{hotel_id}")
async def get_hotel(hotel_id: int, db: SessionDep):
    result = await db.execute(
        select(Hotel).filter(Hotel.hotel_id == hotel_id)
    )
    hotel = result.scalars().first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return hotel

@router.patch("/{hotel_id}")
async def update_hotel(
    hotel_id: int,
    hotel_update: HotelUpdate,
    db: SessionDep,
    current_user: CurretUser
):
    result = await db.execute(
        select(Hotel).filter(
            Hotel.hotel_id == hotel_id,
            Hotel.owner_id == current_user.id 
        )
    )
    hotel = result.scalars().first()

    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found or unauthorized")

    for field, value in hotel_update.model_dump(exclude_unset=True).items():
        setattr(hotel, field, value)

    await db.commit()
    await db.refresh(hotel)
    return hotel

@router.delete("/{hotel_id}")
async def delete_hotel(
    hotel_id: int,
    db: SessionDep,
    current_user: CurretUser
):
    result = await db.execute(
        select(Hotel).filter(
            Hotel.hotel_id == hotel_id,
            Hotel.owner_id == current_user.id
        )
    )
    hotel = result.scalars().first()

    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found or unauthorized")

    await db.delete(hotel)
    await db.commit()
    return {"detail": "Hotel deleted successfully"}
