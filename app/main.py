from pydantic import BaseModel 
from fastapi import FastAPI, APIRouter  
from app.routers import admin, auth, flight_airplane, permissions, roles, hotels, rooms, bookings,flight_airline,flight_create,flight_airport,flight_bookings
from app.database.database import engine, Base 
import app.models  
from app.models.flight_models import Airline,Airport,Airplane,AirplaneSeat,Flight,FlightSeat,FlightBooking,Passenger,SeatAllocation
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
app.include_router(flight_airplane.router,prefix="/airplane",tags=["airplane"])
app.include_router(flight_airline.router,prefix="/airline",tags=["airline"])
app.include_router(flight_create.router,prefix="/flight",tags=["flight"])
app.include_router(flight_airport.router,prefix="/airport",tags=["airport"])
app.include_router(flight_bookings.router,prefix="/flight_booking",tags=["flight_booking"])
# app.include_router(airport.router,prefix="/airport",tags=["airport"])
# app.include_router(flight.router,prefix="/flight",tags=["flights"])
# app.include_router(flight_seat.router,prefix="/seats",tags=["seat"])


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

