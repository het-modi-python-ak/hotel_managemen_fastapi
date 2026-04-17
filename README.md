# hotel_managemen_fastapi




### tech satck
Python 3.11+
FastAPI
SQLAlchemy + Alembic
PostgreSQL
Redis
Celery (worker + beat scheduler)

### Getting Started

    Clone the repo
    Install dependencies: npm install or pip install -r requirements.txt
    Environment Variables: Create a .env file with DATABASE_URL, DATABASE_PASSWORD, DATBASE_HOST,EMAIL,EMAIL_PASSOWRD, and JWT_SECRET.
    Run: npm start or uvicorn main:app 

### API ENDPOINTS 

### ADMIN 
POST admin/assing-role

### AUTH
POST auth/signup
<br> GET auth/verify
<br>POST auth/register
<br>POST auth/login
<br> GET auth

### PERMISSION
<br>POST /permissions
<br>GET /permissions
<br>POST /permissions/assign_permission

### ROLES
<br>POST /roles
<br>GET /roles
<br>GET /roles/users
<br>GET /roles/{role_id}
<br>PATCH /roles/{role_id}
<br>DELETE /roles/{role_id}

### HOTELS
<br>POST /hotels/
<br>GET /hotels/
<br>GET /hotels/my
<br>GET /hotels{hotel_id}
<br>PATCH /hotels/{hotel_id}
<br>DELETE /hotels/{hotel_id}

### ROOMS
<br>POST /rooms/{hotel_id}
<br>GET /rooms/{hotel_id}
<br>PATCH /rooms/{hotel_id}/{room_id}
<br>DELETE /rooms/{hotel_id}/{room_id}

### HOTEL BOOKING 
<br>GET /booking
<br>POST /booking
<br>PATCH /booking/{booking_id}
<br>DELTE /booking/{booking_id}
<br>GET /booking/{booking_id}


### Flights & Schedules

    GET /flights: Search for available flights by origin/destination.
    POST /flights: Add a new flight route and schedule.
    GET /flights/{flight_id}: Get real-time status and aircraft info.

### Flight Bookings

    POST /flights/booking: Reserve a seat on a flight.
    GET /flights/booking/{id}: View boarding pass and itinerary.
    DELETE /flights/booking/{id}: Cancel flight ticket.
