
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from models.user import User
from core.security import hash_password
from fastapi import HTTPException
from core.security import verify_password, create_access_token



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
def login(email: str, password: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid email")

    if not verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Invalid password")

    token = create_access_token({"user_id": user.id})

    return {"access_token": token, "token_type": "bearer"}
