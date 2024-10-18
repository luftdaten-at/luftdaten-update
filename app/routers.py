from fastapi import APIRouter, Request, HTTPException, Header
from fastapi.responses import FileResponse
import hashlib
import os
from typing import List

from utils import calculate_sha256, FileEntry, get_files_with_sha256
from config import Config

router = APIRouter()

@router.get("/download/{filename}")
async def serve_file(filename: str):
    file_path = os.path.join(Config.FIRMWARE_FOLDER, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Datei nicht gefunden")

    sha256_checksum = calculate_sha256(file_path)
    headers = {'sha256_checksum': sha256_checksum}

    return FileResponse(file_path, filename=filename, headers=headers)

@router.get("/file_list", response_model=List[FileEntry])
async def serve_file_list():
    local_folder = Config.FIRMWARE_FOLDER
    file_list = get_files_with_sha256(local_folder)
    return file_list

# TODO: could be a potential security issue
'''
@router.post("/sync_files")
async def sync_files(request: Request, x_filename: str = Header(None)):
    file_data = await request.body()
    filename = x_filename

    if not filename:
        raise HTTPException(status_code=400, detail="Dateiname fehlt in den Anfrage-Headern")

    filename = os.path.basename(filename)

    received_md5_checksum = hashlib.md5(file_data).hexdigest()

    try:
        save_path = os.path.join('.', filename)
        with open(save_path, 'wb') as file:
            file.write(file_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Speichern der Datei auf dem Server: {e}")

    return received_md5_checksum
'''
