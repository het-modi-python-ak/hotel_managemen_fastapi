# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import SQLAlchemyError
# from app.database.database import get_db
# from app.models.flight_models import Flight,Airport,FlightBooking
# from app.core.dependencies import get_current_user
# from app.schemas.schemas import AirportUpdate,FlightCreate,FlightUpdate ,FlightResponse
# from datetime import datetime,timezone
# from typing import List

# router = APIRouter()

# # @router.post("/")
# # def create_booking(seat_id:int, flight_id:int , db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    