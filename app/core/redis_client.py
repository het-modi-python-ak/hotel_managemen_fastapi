import redis

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
)



#booking_lock:{hotel_id}:{room_id}:{check_in}:{check_out}