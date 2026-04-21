from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete  # Added for efficient deletes
from app.database.database import get_db
from app.models.flight_models import Flight, AirplaneSeat, Airplane, FlightSeat
from app.core.dependencies import get_current_user
from datetime import datetime, timezone
from typing import Annotated
from app.models.user import User
from app.schemas.schemas import CreateFlight

SessionDep = Annotated[AsyncSession, Depends(get_db)]
CurretUser = Annotated[User, Depends(get_current_user)]

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_flight(
    data: CreateFlight,
    db: SessionDep,
    current_user: CurretUser
):
    try:
        # Validation Logic
        if data.depart_time >= data.arrival_time:
            raise HTTPException(status_code=400, detail="Arrival must be after departure.")
        
        if data.depart_time < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Departure cannot be in the past.")

        #  Check Airplane Ownership
        airplane_result = await db.execute(
            select(Airplane).filter(
                Airplane.airplane_id == data.airplane_id,
                Airplane.created_by == current_user.id
            )
        )
        airplane = airplane_result.scalars().first()

        if not airplane:
            raise HTTPException(status_code=403, detail="Airplane not found or unauthorized.")

        #  Overlap Check
        overlap_result = await db.execute(
            select(Flight).filter(
                Flight.airplane_id == data.airplane_id,
                Flight.depart_time < data.arrival_time,
                Flight.arrival_time > data.depart_time
            )
        )
        if overlap_result.scalars().first():
            raise HTTPException(status_code=400, detail="Airplane is already scheduled for this time.")

        # Get Airplane Seat Layout
        seat_layout_result = await db.execute(
            select(AirplaneSeat).filter(AirplaneSeat.airplane_id == data.airplane_id)
        )
        airplane_seats = seat_layout_result.scalars().all()
        if not airplane_seats:
            raise HTTPException(status_code=400, detail="Airplane seat layout not found")

        #  Create Flight
        new_flight = Flight(
            flight_number=data.flight_number,
            airplane_id=data.airplane_id,
            source_id=data.source_id,
            destination_id=data.destination_id,
            depart_time=data.depart_time,
            arrival_time=data.arrival_time,
            created_by=current_user.id
        )
        db.add(new_flight)
        await db.flush()  

      
        flight_seats = [
            FlightSeat(
                flight_id=new_flight.flight_id,
                seat_number=s.seat_number,
                seat_class=s.seat_class,
                price=1000, 
                created_by=current_user.id
            )
            for s in airplane_seats
        ]
        db.add_all(flight_seats)
        
        await db.commit()
        return {"message": "Flight created", "flight_id": new_flight.flight_id}
        
    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/")
async def get_all_flights(db: SessionDep):
    result = await db.execute(select(Flight))
    return result.scalars().all()



@router.get("/me")
async def get_my_flights(db: SessionDep, current_user: CurretUser):
    result = await db.execute(select(Flight).filter(Flight.created_by == current_user.id))
    return result.scalars().all()



@router.delete("/{flight_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flight(flight_id: int, db: SessionDep, current_user: CurretUser):
    result = await db.execute(
        select(Flight).filter(Flight.flight_id == flight_id, Flight.created_by == current_user.id)
    )
    flight = result.scalars().first()

    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    try:
        
        await db.execute(delete(FlightSeat).filter(FlightSeat.flight_id == flight_id))
       
        await db.delete(flight)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Delete failed")


@router.get("/search_flight")
async def search_flights(source_id: int, destination_id: int, db: SessionDep):
    result = await db.execute(
        select(Flight).filter(Flight.source_id == source_id, Flight.destination_id == destination_id)
    )
    return result.scalars().all()
