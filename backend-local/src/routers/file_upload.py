from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
import os
import shutil
from typing import List

from kafka import KafkaProducer

from components.file_upload.process_file_stream import process_stream
from resources.kafka import get_producer

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
        for file in files:
            print(f"Processing file: {file.filename}, length: {file.size}")
            validate_file(file)
            process_stream(file.file, file.filename or "", file.size or 0)
            saved_files.append(file.filename)
        return {
            "message": f"Successfully uploaded {len(saved_files)} file(s): {', '.join(saved_files)}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
