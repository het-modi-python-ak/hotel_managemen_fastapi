from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database.database import get_db
from app.models.flight_models import Flight,AirplaneSeat,Airplane,FlightSeat
from app.core.dependencies import get_current_user
# from app.schemas.schemas import AirportUpdate,FlightCreate,FlightUpdate ,FlightResponse
from datetime import datetime,timezone
from typing import List





router = APIRouter()


@router.post("/",status_code=status.HTTP_201_CREATED)

def create_flight(flight_number:str,airplane_id:int,source_id:int,destination_id:int,depart_time,arrival_time,db:Session=Depends(get_db),
                  current_user=Depends(get_current_user)):

                  try:
                      airplane = db.query(Airplane).filter(Airplane.airplane_id==airplane_id,Airplane.created_by==current_user.id).first()
                    
                      if not airplane:
                          raise HTTPException(status_code=403,detail="You can not create flight using another plane")

                      flight = Flight(flight_number=flight_number,airplane_id=airplane_id,source_id=source_id,destination_id=destination_id,arrival_time=arrival_time,created_by=current_user.id) 
                      db.add(flight)
                      db.commit()
                      db.refresh(flight)

                      
                      airplane_seats=db.query(AirplaneSeat).filter(AirplaneSeat.airplane_id==airplane_id).all()
                      
                      
                      

                      if not airplane_seats:
                          raise HTTPException(status_code=400,detail="Airplane seat layout not found")

                      
                      
                      seats = []

                      for seat in airplane_seats:
                          
                          seats.append(FlightSeat(fligght_id = flight.flight_id,seat_number = seat.seat_number,seaat_class=seat.seat_class,price=1000,created_by=current_user.id))
                          db.add_all(seats)
                          db.commit()
                          
                          return {"message":"Flight created successfully","flight_id":flight.flight_id,"seates_generaed":len(seats)}
                          
                          
                  except SQLAlchemyError:
                      db.rollback()
                      raise HTTPException(status_code=500,detail="Erorr creating flight ")
                    
            
            
            
#get
@router.get("/")
def get_all_flights(db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    flights = db.query(Flight).filter(Flight.created_by == current_user.id).all()
    
    if not flights:
        raise HTTPException(status_code=404,detail="No flight found")
    
    return flights



