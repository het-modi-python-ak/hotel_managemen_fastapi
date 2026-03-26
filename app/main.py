from pydantic import BaseModel 
from fastapi import FastAPI, APIRouter  
from routers import admin, auth, permissions, roles ,hotels,rooms,bookings
from database.database import engine, Base 
import models  


app = FastAPI() 

Base.metadata.create_all(bind=engine)  

app.include_router(admin.router, prefix="/admin",tags=["admin"]) # Added prefix for clarity
app.include_router(auth.router, prefix="/auth",tags=["auth"]) 
app.include_router(permissions.router,prefix="/permissions",tags=["permissions"])
app.include_router(roles.router,prefix="/roles",tags=["roles"])
app.include_router(hotels.router,prefix="/hotels",tags=["hotels"])
app.include_router(rooms.router,prefix="/rooms",tags=["rooms"])
app.include_router(bookings.router,prefix="/booking",tags=["booking"])