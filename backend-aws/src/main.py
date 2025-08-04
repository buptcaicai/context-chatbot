import asyncio
import os
import dotenv

from resources.redis import connect_redis, get_redis_client
from resources.SysParam import get_ssm_parameters_async
dotenv.load_dotenv(override=True)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routers.file_upload import router as upload_router
from routers.context_chat import router as chat_router
from resources.sqs import start_sqs_consumers, stop_sqs_consumers

@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_ssm_parameters_async()
    connect_redis()
    print("Redis connected.")
    asyncio.create_task(start_sqs_consumers())
    yield
    print("App shutting down... closing Redis.")
    redis_client = get_redis_client()
    if redis_client:
        await redis_client.aclose()
    await stop_sqs_consumers()

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
