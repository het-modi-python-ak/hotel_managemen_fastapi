# hotel_managemen_fastapi

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
