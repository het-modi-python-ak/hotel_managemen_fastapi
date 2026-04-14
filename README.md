# hotel_managemen_fastapi

#API ENDPOINTS 

ADMIN 
POST admin/assing-role

AUTH
POST auth/signup
GET auth/verify
POST auth/register
POST auth/login
GET auth

PERMISSION
POST /permissions
GET /permissions
POST /permissions/assign_permission


ROLES
POST /roles
GET /roles
GET /roles/users
GET /roles/{role_id}
PATCH /roles/{role_id}
DELETE /roles/{role_id}


HOTELS
POST /hotels/
GET /hotels/
GET /hotels/my
GET /hotels{hotel_id}
PATCH /hotels/{hotel_id}
DELETE /hotels/{hotel_id}


ROOMS
POST /rooms/{hotel_id}
GET /rooms/{hotel_id}
PATCH /rooms/{hotel_id}/{room_id}
DELETE /rooms/{hotel_id}/{room_id}


HOTEL BOOKING 
GET /booking
POST /booking
PATCH /booking/{booking_id}
DELTE /booking/{booking_id}
GET /booking/{booking_id}
