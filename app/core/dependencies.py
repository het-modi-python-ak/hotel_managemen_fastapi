from jose import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database.database import get_db
from models.user import User

SECRET_KEY = "secretkey"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")

    except:
        raise HTTPException(status_code=401, detail="Invalid Token")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


def require_permission(permission_name: str):

    def permission_checker(current_user: User = Depends(get_current_user)):

        for role in current_user.roles:
            for perm in role.permissions:
                if perm.name == permission_name:
                    return True

        raise HTTPException(status_code=403, detail="Permission denied")

    return permission_checker