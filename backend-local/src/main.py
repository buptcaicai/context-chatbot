import asyncio
import os
import dotenv
dotenv.load_dotenv(override=True)
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from resources.kafka import init_kafka, shutdown_kafka
from resources.redis import connect_redis, get_redis_client 
from routers.file_upload import router as upload_router
from routers.context_chat import router as chat_router
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create the Kafka producer at startup
    await init_kafka()
    connect_redis()
    print("Kafka producer started.")
    yield
    # Cleanup on shutdown
    print("App shutting down... closing Kafka producer.")
    redis_client = get_redis_client()
    if redis_client:
        await redis_client.aclose()
    await shutdown_kafka()

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
app.include_router(prefix="/chat", router=chat_router)
