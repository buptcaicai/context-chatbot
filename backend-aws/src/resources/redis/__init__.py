import redis.asyncio as redis
import os

__redis_client: redis.Redis | None = None

def connect_redis():
    global __redis_client
    __redis_client = redis.Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT")), decode_responses=True) # type: ignore

def get_redis_client():
    global __redis_client
    return __redis_client
