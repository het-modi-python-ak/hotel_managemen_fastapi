Hotel & Flight Booking System (FastAPI)

A scalable backend system for managing hotel and flight bookings, built with FastAPI.
The project demonstrates production-style backend architecture including authentication, role-based access control, background task processing, and notification scheduling.

---

Features

Authentication & Authorization

- JWT-based authentication
- Email verification during registration
- Role-Based Access Control (RBAC)
- Permission management system
- Admin role assignment

Hotel Management

- Create and manage hotels
- Create and manage hotel rooms
- Hotel booking system
- Booking updates and cancellations
- View user bookings

Flight Management

- Create airports and airlines
- Create airplanes and flight schedules
- Flight seat booking system
- Prevent double seat booking
- View and cancel flight reservations

Notifications

- Booking confirmation notifications
- Booking cancellation notifications
- Flight reminder notifications before departure
- Background task processing using Celery

Background Processing

- Asynchronous task processing
- Scheduled reminder notifications

---

Tech Stack

Technology| Purpose
Python 3.11+| Programming Language
FastAPI| Backend API framework
MySQL| Relational database
SQLAlchemy| ORM for database interaction
Alembic| Database migrations
Redis| Message broker and caching
Celery| Background task processing
JWT| Authentication

---

System Architecture

The system follows a modular backend architecture:

Client
   ↓
FastAPI REST API
   ↓
MySQL Database
   ↓
Celery Workers
   ↓
Redis Broker

Flow

1. User registers and logs in using JWT authentication.
2. Admin creates hotels, rooms, airlines, airports, and flights.
3. Users browse hotels or flights.
4. Users book rooms or flight seats.
5. Booking data is stored in MySQL.
6. Celery schedules notification tasks.
7. Users receive confirmation and reminder notifications.


---

Getting Started

1. Clone Repository

git clone https://github.com/yourusername/hotel_management_fastapi.git
cd hotel_management_fastapi

---

2. Install Dependencies

pip install -r requirements.txt

---

3. Setup Environment Variables

Create a ".env" file in the project root.

DATABASE_URL=
DATABASE_HOST=
DATABASE_PASSWORD=

JWT_SECRET=

EMAIL=
EMAIL_PASSWORD=

REDIS_URL=redis://localhost:6379/0

---

4. Run Database Migrations

alembic upgrade head

---

5. Start FastAPI Server

uvicorn main:app --reload

Server runs at:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs

---

6. Start Background Workers

Start Redis first.

Then run Celery worker:

celery -A app.core.celery_app worker --loglevel=info

Start Celery Beat scheduler:

celery -A app.core.celery_app beat --loglevel=info

---

API Endpoints

Admin

Assign role to user

POST /admin/assign-role

---

Authentication

Method| Endpoint| Description
POST| /auth/signup| Create account
GET| /auth/verify| Verify email
POST| /auth/register| Register user
POST| /auth/login| Login user
GET| /auth| Get authenticated user

---

Permissions

Method| Endpoint
POST| /permissions
GET| /permissions
POST| /permissions/assign_permission

---

Roles

Method| Endpoint
POST| /roles
GET| /roles
GET| /roles/users
GET| /roles/{role_id}
PATCH| /roles/{role_id}
DELETE| /roles/{role_id}

---

Hotels

Method| Endpoint
POST| /hotels
GET| /hotels
GET| /hotels/my
GET| /hotels/{hotel_id}
PATCH| /hotels/{hotel_id}
DELETE| /hotels/{hotel_id}

---

Rooms

Method| Endpoint
POST| /rooms/{hotel_id}
GET| /rooms/{hotel_id}
PATCH| /rooms/{hotel_id}/{room_id}
DELETE| /rooms/{hotel_id}/{room_id}

---

Hotel Booking

Method| Endpoint
GET| /booking
POST| /booking
GET| /booking/{booking_id}
PATCH| /booking/{booking_id}
DELETE| /booking/{booking_id}

---

Flights

Method| Endpoint| Description
GET| /flights| Search available flights
POST| /flights| Create flight schedule
GET| /flights/{flight_id}| Get flight details

---

Flight Bookings

Method| Endpoint| Description
POST| /flights/booking| Book flight seat
GET| /flights/booking/{id}| View flight booking
DELETE| /flights/booking/{id}| Cancel booking

---

Notifications

The system automatically sends:

- Booking confirmation emails
- Booking cancellation notifications
- Flight departure reminders

Reminder jobs are processed by Celery workers and scheduled using Celery Beat.

---

Future Improvements

Possible enhancements for the system:

- Payment gateway integration
- Real-time seat availability updates
- Push notifications
- Distributed worker scaling
- Analytics dashboard for bookings

---

License

This project is intended for educational and demonstration purposes.
