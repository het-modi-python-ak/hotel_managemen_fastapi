from pydantic import BaseModel 
from fastapi import FastAPI, APIRouter  
from routers import admin, auth, permissions, roles   
from database.database import engine, Base 
import models  

# This line creates the actual FastAPI application instance
app = FastAPI() 

# This ensures the database tables are created (assuming models and database setup are correct)
Base.metadata.create_all(bind=engine)  

# You can still define a 'router' for main routes if you want, but it's not strictly necessary for this file
# main_router = APIRouter() 

# Include your specific routers in the main 'app' instance
app.include_router(admin.router, prefix="/admin") # Added prefix for clarity
app.include_router(auth.router, prefix="/auth") 
app.include_router(permissions.router,prefix="/permissions")
app.include_router(roles.router,prefix="/roles")
# Include other routers similarly:
# app.include_router(permissions.router)
# app.include_router(roles.router)

# Example of a route defined directly in this main file using the 'app' instance
@app.get("/hello") 
def print_hello(): 
    print("in the user function") 
    return {"message":"how are you "}
