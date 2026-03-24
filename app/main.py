from pydantic import BaseModel
from fastapi import FastAPI
app = FastAPI()

@app.get("/hello")
def print_hello():
    print("in the user function")
    return {"message":"how are you "}