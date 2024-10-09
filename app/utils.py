from pydantic import BaseModel
import datetime
import hashlib
import os

def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as firmware_file:
        for chunk in iter(lambda: firmware_file.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

class FileEntry(BaseModel):
    relative_path: str
    sha256_checksum: str
    last_update: str

def get_files_with_sha256(folder):
    file_list = []
    for root, dirs, files in os.walk(folder):
        for filename in files:
            filepath = os.path.join(root, filename)
            sha256_checksum = calculate_sha256(filepath)
            last_update = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
            last_update_str = last_update.strftime('%Y-%m-%d %H:%M:%S')
            relative_path = os.path.relpath(filepath, folder).replace('\\', '/')
            file_entry = FileEntry(
                relative_path=relative_path,
                sha256_checksum=sha256_checksum,
                last_update=last_update_str
            )
            file_list.append(file_entry)
    return file_list