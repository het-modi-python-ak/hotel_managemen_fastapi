from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database.database import get_db
from app.models.flight_models import Airplane,Airline,FlightSeat,AirplaneSeat
from app.core.dependencies import get_current_user
from enum import Enum
from pydantic import BaseModel
from app.schemas.schemas import SeatCategory,CreateAirplane

from typing import Annotated
from app.models.user import User

SessionDep = Annotated[Session, Depends(get_db)]
CurretUser = Annotated[User,Depends(get_current_user)]


router = APIRouter()



@router.post("/", status_code=status.HTTP_201_CREATED)
def create_airplane(
   
    data : CreateAirplane,
    db: SessionDep,
    current_user:CurretUser
):
    
    model = data.model
    total_seats = data.total_seats
    airline_id = data.airline_id
    total_business_seat = data.total_business_seat
    total_economy_seat = data.total_economy_seat
    total_premium_seat = data.total_premium_seat


    if total_seats <= 0:
        raise HTTPException(
            status_code=400,
            detail="Total seats must be greater than 0"
        )

    if total_business_seat + total_economy_seat + total_premium_seat != total_seats:
        raise HTTPException(
            status_code=412,
            detail="Seat category totals must equal total seats"
        )

    try:

        airline = db.query(Airline).filter(
            Airline.airline_id == airline_id,
            Airline.created_by == current_user.id
        ).first()

        if not airline:
            raise HTTPException(
                status_code=403,
                detail="You cannot add airplane to another user's airline"
            )

        airplane = Airplane(
            model=model,
            total_seats=total_seats,
            airline_id=airline_id,
            created_by=current_user.id
        )

        db.add(airplane)
        db.commit()
        db.refresh(airplane)

        seats = []

        # BUSINESS seats
        for i in range(total_business_seat):
            seats.append(
                AirplaneSeat(
                    airplane_id=airplane.airplane_id,
                    seat_number=f"B{i+1}",
                    seat_class=SeatCategory.BUSINESS.value,
                    created_by=current_user.id
                )
            )

        # PREMIUM seats
        for i in range(total_premium_seat):
            seats.append(
                AirplaneSeat(
                    airplane_id=airplane.airplane_id,
                    seat_number=f"P{i+1}",
                    seat_class=SeatCategory.PREMIUM.value,
                    created_by=current_user.id
                )
            )

        # ECONOMY seats
        for i in range(total_economy_seat):
            seats.append(
                AirplaneSeat(
                    airplane_id=airplane.airplane_id,
                    seat_number=f"E{i+1}",
                    seat_class=SeatCategory.ECONOMY.value,
                    created_by=current_user.id
                )
            )

        db.add_all(seats)
        db.commit()

        return {
            "message": "Airplane created successfully with seat layout",
            "airplane_id": airplane.airplane_id,
            "total_seats_created": len(seats)
        }

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error occurred while creating airplane {e}"
        )
        
        
        

@router.get("/")
def get_all_airplanes(
    db: SessionDep,
   
):
    try:
        airplanes = db.query(Airplane).all()
        if not airplanes:
            raise HTTPException(status_code=404, detail="No airplanes found")
        return airplanes
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error fetching airplanes")



@router.get("/{airplane_id}")
def get_airplane(
    airplane_id: int,
    db: SessionDep,
  
):
    try:
        airplane = db.query(Airplane).filter(Airplane.airplane_id == airplane_id).first()
        if not airplane:
            raise HTTPException(status_code=404, detail="Airplane not found")
        return airplane
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error retrieving airplane details")




class UpdateAirple(BaseModel):
    airplane_id: int
    model: str | None = None,
    total_seats: int | None = None


@router.patch("/{airplane_id}")
def update_airplane(

    data : UpdateAirple,
    db: SessionDep,
    current_user = Depends(get_current_user)
):
    try:
        
        airplane_id = data.airplane_id
        model = data.model
        total_seats = data.total_seats
        
        
        
        airplane = db.query(Airplane).filter(Airplane.airplane_id == airplane_id,Airplane.created_by==current_user.id).first()
        if not airplane:
            raise HTTPException(status_code=404, detail="Airplane not found")

        if total_seats is not None and total_seats <= 0:
            raise HTTPException(status_code=400, detail="Total seats must be greater than 0")

        if model:
            airplane.model = model
        if total_seats:
            airplane.total_seats = total_seats

        db.commit()
        db.refresh(airplane)
        return airplane
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error updating airplane")




@router.delete("/{airplane_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_airplane(
    airplane_id: int,
    db: SessionDep,
    current_user = Depends(get_current_user)
):
    try:
        airplane = db.query(Airplane).filter(Airplane.airplane_id == airplane_id, Airplane.created_by == current_user.id).first()
        if not airplane:
            raise HTTPException(status_code=404, detail="Airplane not found ")
        
        airplane = db.query(Airplane).filter(Airplane.airplane_id == airplane_id).first()
        if not airplane:
            raise HTTPException(status_code=404, detail="Airplane not found")

        db.delete(airplane)
        db.commit()
        return None  
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error deleting airplane")



