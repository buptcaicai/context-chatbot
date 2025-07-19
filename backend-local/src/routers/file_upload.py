import asyncio
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
import os
import shutil
from typing import List

from kafka import KafkaProducer

from components.file_upload import FileContentResponse
from components.file_upload.process_file_stream import process_stream
from resources.kafka import get_producer
from resources.redis import get_redis_client

ALLOWED_EXTENSIONS = {".txt"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes

router = APIRouter()

def validate_file(file: UploadFile):
    """Validate file extension and size."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a filename.")
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, detail=f"File '{file.filename}' has an invalid extension."
        )
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, detail=f"File '{file.filename}' exceeds 5MB limit."
        )
    return ext


@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    try:
        saved_files = []
        futures = []
        msg = ""
        r = get_redis_client()
        for file in files:
            print(f"Processing file: {file.filename}, length: {file.size}")
            if r is not None and await r.zscore("file-injested-zset", f"{file.filename}::{file.size}") is not None:
                msg += f"{file.filename} already injested\n"
                continue
            validate_file(file)
            future = process_stream(file.file, file.filename or "", file.size or 0)
            if future is not None:
                futures.append(future)
            saved_files.append(file.filename)
        responses: list[FileContentResponse] = await asyncio.gather(*futures)
        msg += "\n".join([f"{response.file_name}: {response.status}" for response in responses])
        return {"message": f"{msg}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get-file-injested")
async def get_file_injested():
    r = get_redis_client()
    if r is not None:
        injested_files = await r.zrange("file-injested-zset", 0, -1)
        return {"message": injested_files}
    else:
        raise HTTPException(status_code=500, detail="Redis client is not initialized")
