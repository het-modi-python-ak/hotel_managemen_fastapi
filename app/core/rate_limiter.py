import time 
from fastapi import HTTPException,status
from app.core.redis_client import redis_client
import uuid


request_store={}



def fixed_window_rate_limit(user_id:int,endpoint:str,limit:int=5,window:int=10):
    current_window = int(time.time()//window)
    
    key =  f"rate_limit:{user_id}:{endpoint}:{current_window}"
    
    current_count = redis_client.incr(key)
    
   
    
    if current_count==1:
        redis_client.expire(key,window)
        
    if current_count>limit:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,detail="Too many requests.Please try again later")
 
    




def sliding_window_rate_limiter(user_id: int, endpoint: str, limit: int = 5, window: int = 60):
    key = f"rate_limit:{user_id}:{endpoint}"
    now = time.time()  
    window_start = now - window

    
    pipe = redis_client.pipeline()

    #  Remove old requests outside the current window
    pipe.zremrangebyscore(key, 0, window_start)
    
    #  Count current requests in the window
    pipe.zcard(key)
    
    # Add current request with a UNIQUE member (timestamp + uuid)
    unique_id = f"{now}-{uuid.uuid4()}"
    pipe.zadd(key, {unique_id: now})
    
   
    pipe.expire(key, window)
    
    # Execute pipeline
    results = pipe.execute()
    request_count = results[1]

    if request_count >= limit:
        raise HTTPException(
            status_code=429, 
            detail="Too many requests. Please try again."
        )



#zset = score + member 
#scor = timestamp memmber = uniquer request Id