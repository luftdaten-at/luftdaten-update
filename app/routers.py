from fastapi import APIRouter, Request, HTTPException, Header
from fastapi.responses import FileResponse
import os
from typing import List

from utils import calculate_sha256, FileEntry, get_files_with_sha256, get_folders, FolderEntry
from config import Config
from dirTree import FolderEntry


router = APIRouter()

@router.get("/download")
async def serve_file(filename: str):
    file_path = os.path.join(Config.FIRMWARE_FOLDER, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Datei nicht gefunden")

    sha256_checksum = calculate_sha256(file_path)
    headers = {'sha256_checksum': sha256_checksum}

    return FileResponse(file_path, filename=filename, headers=headers)

@router.get("/file_list/{folder}")
async def serve_file_list(folder: str):
    local_folder = os.path.join(Config.FIRMWARE_FOLDER, folder)

    if not os.path.exists(local_folder):
        raise HTTPException(status_code=404, detail="Ordner nicht gefunden")        

    folder_entry = FolderEntry(local_folder)

    return folder_entry.to_dict()

@router.get("/latest_version/{model_id}")
async def get_latest_firmware_version_for_device(model_id: str):
    path = os.path.join(Config.FIRMWARE_FOLDER)

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Device Id: {model_id}, existiert nicht")

    firmware_versions = [f for f in os.listdir(path) if f.split('_')[0] == model_id]

    if not firmware_versions:
        raise HTTPException(status_code=404, detail=f"Keine Version für Geräte mit Device Id: {model_id} gefunden")

    latest_version = max(firmware_versions)

    return latest_version

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
