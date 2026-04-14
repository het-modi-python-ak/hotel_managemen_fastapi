from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database.database import get_db
from app.models.flight_models import Airport 
from app.core.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter()


class CreateAirport(BaseModel):
    code:str
    name:str
    location:str
    country:str



@router.post("/") 
def create_airport(
    # code:str,name:str,location:str,country:str
                   data : CreateAirport,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    try:
        
        code = data.code
        name = data.name
        location = data.location
        country = data.country
        
        existing_airport=db.query(Airport).filter(Airport.code==code).first()

        if existing_airport:
            raise HTTPException(status_code=400,detail="Airport code already exists")

        
        airport = Airport(code=code.upper(),name=name,location=location,country=country,created_by = current_user.id)
        db.add(airport)
        db.commit()
        db.refresh(airport)

        return airport
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500,detail="Error creating airport")



from typing import List

# GET: Retrieve all airports
@router.get("/")
def get_airports(db: Session = Depends(get_db)):
    return db.query(Airport).all()

# GET: Retrieve a single airport by its code
@router.get("/{airport_code}")
def get_airport(airport_code: str, db: Session = Depends(get_db)):
    airport = db.query(Airport).filter(Airport.code == airport_code).first()
    if not airport:
        raise HTTPException(status_code=404, detail="Airport not found")
    return airport

