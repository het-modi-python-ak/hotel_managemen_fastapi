
from fastapi import APIRouter, Depends,BackgroundTasks
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.user import User
from app.models.user_email import User2
from app.core.security import hash_password
from fastapi import HTTPException
from app.core.security import verify_password, create_access_token
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi import Depends
from typing import Annotated
from app.core.dependencies import get_current_user
from app.core.redis_client import redis_client
from app.core.security import generate_email_token
from app.services.email_service import send_verification_email






router = APIRouter()







@router.post("/signup")
async def signup(
    background_tasks: BackgroundTasks, 
    name: str, 
    email: str, 
    phone: str, 
    password: str, 
    db: Session = Depends(get_db)
):
   
    existing_user = db.query(User2).filter(User2.email == email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already exists")

    new_user = User2(
        name=name,
        email=email,
        phone=phone,
        password=hash_password(password),
        is_verified=False
    )

    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    
    token = generate_email_token()
    
    redis_client.setex(f"email_verify:{token}", 900, new_user.id)

   
    background_tasks.add_task(send_verification_email, new_user.email, token)

    return {"message": "Verification email sent"}








@router.get("/verify-email")
def verify_email(token:str,db:Session= Depends(get_db)):
    user_id = redis_client.get(f"email_verify:{token}")

    if not user_id:
        raise HTTPException(status_code=400,detail="Invaild or expired token")
    user = db.query(User2).filter(User2.id==int(user_id)).first()
    
    if not user:
        raise HTTPException(status_code=404,detail="Usernot found")
    user.is_verified=True
    
    db.commit()
    
    redis_client.delete(f"email_verify : {token}")
    return {"message":"Email verified successfully"}


    



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
    
    user2 = db.query(User2).filter(User2.email==data.username).first()
   

    if not user and not user2:
        raise HTTPException(status_code=400, detail="Invalid email or password") 
    
    if not user2.is_verified:   #updated user2
        raise HTTPException(status_code=403,detail="Please verify your email")
    
    if not verify_password(data.password, user2.password):   # update d the user2
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    
    
    

   
    token = create_access_token({"user_id": user2.id})
    return {"access_token": token, "token_type": "bearer"}





@router.get("/")
def get_current_user(db : Session =  Depends(get_db), current_user=Depends(get_current_user)):
    user = db.query(User).filter(User.id == current_user.id).first()
    return { "current user is " ,user.name }
