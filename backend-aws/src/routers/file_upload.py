import asyncio
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
import os
import shutil
from typing import List

from components.file_upload.process_file_stream import process_stream
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
        msg = ""
        r = get_redis_client()
        for file in files:
            print(f"Processing file: {file.filename}, length: {file.size}")
            if r is not None and await r.zscore("file-ingested-zset", f"{file.filename}::{file.size}") is not None:
                msg += f"{file.filename} already ingested\n"
                continue
            validate_file(file)
            await process_stream(file.file, file.filename or "", file.size or 0)
            saved_files.append(file.filename)
        msg += "\n".join([f"{name} is succesfully ingested" for name in saved_files])
        return {"message": f"{msg}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get-file-ingested")
async def get_file_ingested():
    print(f"before get_redis_client")
    r = get_redis_client()
    print(f"after get_redis_client")
    if r is not None:
        print(f"before zrange")
        ingested_files = await r.zrange("file-ingested-zset", 0, -1)
        print(f"after zrange")
        return {"message": ingested_files}
    else:
        raise HTTPException(status_code=500, detail="Redis client is not initialized")
