from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database.database import get_db
from app.models.flight_models import Airport 
from app.core.dependencies import get_current_user
from pydantic import BaseModel
from app.schemas.schemas import CreateAirport

from typing import Annotated
from app.models.user import User

SessionDep = Annotated[Session, Depends(get_db)]
CurretUser = Annotated[User,Depends(get_current_user)]


router = APIRouter()





@router.post("/") 
def create_airport(
    # code:str,name:str,location:str,country:str
                   data : CreateAirport,db:SessionDep,current_user:CurretUser):
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
def get_airports(db: SessionDep):
    return db.query(Airport).all()

# GET: Retrieve a single airport by its code
@router.get("/{airport_code}")
def get_airport(airport_code: str, db: SessionDep):
    airport = db.query(Airport).filter(Airport.code == airport_code).first()
    if not airport:
        raise HTTPException(status_code=404, detail="Airport not found")
    return airport

