import os
import dotenv
dotenv.load_dotenv(override=True)
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from resources.kafka import create_producer, get_producer
from resources.redis import connect_redis, get_redis_client 
from routers.file_upload import router as upload_router
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create the Kafka producer at startup
    create_producer()
    connect_redis()
    print("Kafka producer started.")
    yield
    # Cleanup on shutdown
    print("App shutting down... closing Kafka producer.")
    producer = get_producer()
    if producer:
        producer.flush()
        producer.close()
    redis_client = get_redis_client()
    if redis_client:
        redis_client.close()

app = FastAPI(lifespan=lifespan)

cors_origins: list[str] = []
if os.getenv("CORS_ORIGINS"):
    cors_origins = os.getenv("CORS_ORIGINS").split(",") # type: ignore

print(f"CORS_ORIGINS: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(prefix="/files", router=upload_router)
