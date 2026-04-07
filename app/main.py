from pydantic import BaseModel 
from fastapi import FastAPI, APIRouter  
from app.routers import admin, auth, permissions, roles, hotels, rooms, bookings
from app.database.database import engine, Base 
import app.models  
from app.models.flight_models import Airport,Flight,Seat,FlightBooking,Passenger,SeatAllocation
from app.middleware.logging import LoggingMiddleware



app = FastAPI() 

app.add_middleware(LoggingMiddleware)



Base.metadata.create_all(bind=engine)  

app.include_router(admin.router, prefix="/admin",tags=["admin"]) # Added prefix for clarity
app.include_router(auth.router, prefix="/auth",tags=["auth"]) 
app.include_router(permissions.router,prefix="/permissions",tags=["permissions"])
app.include_router(roles.router,prefix="/roles",tags=["roles"])
app.include_router(hotels.router,prefix="/hotels",tags=["hotels"])
app.include_router(rooms.router,prefix="/rooms",tags=["rooms"])
app.include_router(bookings.router,prefix="/booking",tags=["booking"])

# from fastapi import FastAPI, Request,Response,Cookie
# from typing import Annotated
# app = FastAPI()
# @app.get("/all-headers")
# async def get_all_headers(request: Request,response : Response):
#     response.set_cookie(key="fakesession", value="fake-cookie-session-value")
    
#     return request.headers  # Returns a dictionary-like object of all headers



# @app.get("/cookie")
# def func(fakesession : Annotated[str | None, Cookie()] = None):
#     return   {"session_value" : fakesession}
# @app.get("/delete-cookie")

# def delete_cookie(response: Response):
#     response.delete_cookie(key="fakesession")
#     return {"message": "Cookie deleted"}

