
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from models.user import User
from core.security import hash_password
from fastapi import HTTPException
from core.security import verify_password, create_access_token
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi import Depends
from typing import Annotated
from core.dependencies import get_current_user

router = APIRouter()


@router.post("/register")
def register(name: str, email: str, phone: str, password: str, db: Session = Depends(get_db)):

    user = User(
        name=name,
        email=email,
        phone=phone,
        password=hash_password(password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User created"}


@router.post("/login")
def login(data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
   
    user = db.query(User).filter(User.email == data.username).first()
   

    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password") 
    
    
    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

   
    token = create_access_token({"user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/")
def get_current_user(db : Session =  Depends(get_db), current_user=Depends(get_current_user)):
    user = db.query(User).filter(User.id == current_user.id).first()
    return { "current user is " ,user.name }
