import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from fastapi.testclient import TestClient
from fastapi import HTTPException

# Import the app and router
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from main import app
from routers import router
from dirTree import FolderEntry
from config import Config


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def temp_firmware_dir():
    """Create a temporary firmware directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_file(temp_firmware_dir):
    """Create a sample file for testing."""
    file_path = os.path.join(temp_firmware_dir, "test_file.bin")
    with open(file_path, "wb") as f:
        f.write(b"test file content")
    return file_path, "test_file.bin"


@pytest.fixture
def sample_folder_structure(temp_firmware_dir):
    """Create a sample folder structure for testing."""
    folder_path = os.path.join(temp_firmware_dir, "1_1_5_10")
    os.makedirs(folder_path, exist_ok=True)
    
    # Create some files in the folder
    file1 = os.path.join(folder_path, "file1.txt")
    file2 = os.path.join(folder_path, "file2.txt")
    with open(file1, "w") as f:
        f.write("content1")
    with open(file2, "w") as f:
        f.write("content2")
    
    return folder_path, "1_1_5_10"


class TestDownloadEndpoint:
    """Test cases for the /download endpoint."""
    
    def test_download_file_success(self, client, temp_firmware_dir, sample_file):
        """Test successful file download."""
        file_path, filename = sample_file
        
        with patch.object(Config, 'FIRMWARE_FOLDER', temp_firmware_dir):
            response = client.get(f"/download?filename={filename}")
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/octet-stream"
            assert "sha256_checksum" in response.headers
            assert response.content == b"test file content"
    
    def test_download_file_not_found(self, client, temp_firmware_dir):
        """Test file download when file doesn't exist."""
        with patch.object(Config, 'FIRMWARE_FOLDER', temp_firmware_dir):
            response = client.get("/download?filename=nonexistent.bin")
            
            assert response.status_code == 404
            assert "Datei nicht gefunden" in response.json()["detail"]
    
    def test_download_file_with_sha256(self, client, temp_firmware_dir):
        """Test that SHA256 checksum is correctly calculated and returned."""
        import hashlib
        
        # Create a file with known content
        filename = "test.bin"
        file_path = os.path.join(temp_firmware_dir, filename)
        content = b"test content for sha256"
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Calculate expected SHA256
        expected_sha256 = hashlib.sha256(content).hexdigest()
        
        with patch.object(Config, 'FIRMWARE_FOLDER', temp_firmware_dir):
            response = client.get(f"/download?filename={filename}")
            
            assert response.status_code == 200
            assert response.headers["sha256_checksum"] == expected_sha256
    
    def test_download_file_empty_filename(self, client, temp_firmware_dir):
        """Test download with empty filename."""
        with patch.object(Config, 'FIRMWARE_FOLDER', temp_firmware_dir):
            response = client.get("/download?filename=")
            
            # Should return 404 since empty filename won't match any file
            assert response.status_code == 404


class TestFileListEndpoint:
    """Test cases for the /file_list/{folder} endpoint."""
    
    def test_file_list_success(self, client, temp_firmware_dir, sample_folder_structure):
        """Test successful file list retrieval."""
        folder_path, folder_name = sample_folder_structure
        
        with patch.object(Config, 'FIRMWARE_FOLDER', temp_firmware_dir):
            response = client.get(f"/file_list/{folder_name}")
            
            assert response.status_code == 200
            data = response.json()
            assert "path" in data
            assert "childs" in data
            assert "md5_checksum" in data
            # Should have at least 2 files
            assert len(data["childs"]) >= 2
    
    def test_file_list_folder_not_found(self, client, temp_firmware_dir):
        """Test file list when folder doesn't exist."""
        with patch.object(Config, 'FIRMWARE_FOLDER', temp_firmware_dir):
            response = client.get("/file_list/nonexistent_folder")
            
            assert response.status_code == 404
            assert "Ordner nicht gefunden" in response.json()["detail"]
    
    def test_file_list_empty_folder(self, client, temp_firmware_dir):
        """Test file list for an empty folder."""
        folder_name = "empty_folder"
        folder_path = os.path.join(temp_firmware_dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        
        with patch.object(Config, 'FIRMWARE_FOLDER', temp_firmware_dir):
            response = client.get(f"/file_list/{folder_name}")
            
            assert response.status_code == 200
            data = response.json()
            assert "childs" in data
            assert len(data["childs"]) == 0
    
    def test_file_list_nested_structure(self, client, temp_firmware_dir):
        """Test file list with nested folder structure."""
        folder_name = "nested_folder"
        folder_path = os.path.join(temp_firmware_dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        
        # Create nested structure
        subfolder = os.path.join(folder_path, "subfolder")
        os.makedirs(subfolder, exist_ok=True)
        
        file1 = os.path.join(folder_path, "file1.txt")
        file2 = os.path.join(subfolder, "file2.txt")
        
        with open(file1, "w") as f:
            f.write("content1")
        with open(file2, "w") as f:
            f.write("content2")
        
        with patch.object(Config, 'FIRMWARE_FOLDER', temp_firmware_dir):
            response = client.get(f"/file_list/{folder_name}")
            
            assert response.status_code == 200
            data = response.json()
            assert "childs" in data
            # Should have at least the file and subfolder
            assert len(data["childs"]) >= 1


class TestLatestVersionEndpoint:
    """Test cases for the /latest_version/{model_id} endpoint."""
    
    def test_latest_version_success(self, client, temp_firmware_dir):
        """Test successful latest version retrieval."""
        # Create multiple firmware versions
        versions = ["1_1_5_10", "1_1_5_11", "1_1_5_12", "1_1_5_14"]
        for version in versions:
            os.makedirs(os.path.join(temp_firmware_dir, version), exist_ok=True)
        
        with patch.object(Config, 'FIRMWARE_FOLDER', temp_firmware_dir):
            response = client.get("/latest_version/1")
            
            assert response.status_code == 200
            # Should return the latest version (1_1_5_14)
            # FastAPI JSON-encodes string responses, so use json() instead of text
            assert response.json() == "1_1_5_14"
    
    def test_latest_version_not_found(self, client, temp_firmware_dir):
        """Test latest version when model_id doesn't exist."""
        # Create some firmware versions for different model
        os.makedirs(os.path.join(temp_firmware_dir, "2_1_5_0"), exist_ok=True)
        
        with patch.object(Config, 'FIRMWARE_FOLDER', temp_firmware_dir):
            response = client.get("/latest_version/999")
            
            assert response.status_code == 404
            assert "Keine Version für Geräte mit Device Id: 999 gefunden" in response.json()["detail"]
    
    def test_latest_version_single_version(self, client, temp_firmware_dir):
        """Test latest version when only one version exists."""
        os.makedirs(os.path.join(temp_firmware_dir, "1_1_5_10"), exist_ok=True)
        
        with patch.object(Config, 'FIRMWARE_FOLDER', temp_firmware_dir):
            response = client.get("/latest_version/1")
            
            assert response.status_code == 200
            # FastAPI JSON-encodes string responses, so use json() instead of text
            assert response.json() == "1_1_5_10"
    
    def test_latest_version_complex_versions(self, client, temp_firmware_dir):
        """Test latest version with complex version numbers."""
        versions = ["1_1_5_9", "1_1_5_10", "1_1_5_11", "1_1_5_12", "1_1_5_13", "1_1_5_14"]
        for version in versions:
            os.makedirs(os.path.join(temp_firmware_dir, version), exist_ok=True)
        
        with patch.object(Config, 'FIRMWARE_FOLDER', temp_firmware_dir):
            response = client.get("/latest_version/1")
            
            assert response.status_code == 200
            # FastAPI JSON-encodes string responses, so use json() instead of text
            assert response.json() == "1_1_5_14"
    
    def test_latest_version_multiple_models(self, client, temp_firmware_dir):
        """Test latest version when multiple models exist."""
        # Create versions for different models
        model1_versions = ["1_1_5_10", "1_1_5_11"]
        model2_versions = ["2_1_5_0", "2_1_5_2"]
        
        for version in model1_versions + model2_versions:
            os.makedirs(os.path.join(temp_firmware_dir, version), exist_ok=True)
        
        with patch.object(Config, 'FIRMWARE_FOLDER', temp_firmware_dir):
            # Test model 1
            response1 = client.get("/latest_version/1")
            assert response1.status_code == 200
            # FastAPI JSON-encodes string responses, so use json() instead of text
            assert response1.json() == "1_1_5_11"
            
            # Test model 2
            response2 = client.get("/latest_version/2")
            assert response2.status_code == 200
            # FastAPI JSON-encodes string responses, so use json() instead of text
            assert response2.json() == "2_1_5_2"
    
    def test_latest_version_firmware_folder_not_exists(self, client):
        """Test latest version when firmware folder doesn't exist."""
        with patch.object(Config, 'FIRMWARE_FOLDER', "/nonexistent/path"):
            response = client.get("/latest_version/1")
            
            assert response.status_code == 404
            assert "existiert nicht" in response.json()["detail"]
    
    def test_latest_version_version_ordering(self, client, temp_firmware_dir):
        """Test that version ordering works correctly (not just lexicographic)."""
        # Create versions that would be incorrectly ordered lexicographically
        versions = ["1_1_5_2", "1_1_5_10", "1_1_5_3"]
        for version in versions:
            os.makedirs(os.path.join(temp_firmware_dir, version), exist_ok=True)
        
        with patch.object(Config, 'FIRMWARE_FOLDER', temp_firmware_dir):
            response = client.get("/latest_version/1")
            
            assert response.status_code == 200
            # Should return 1_1_5_10 (not 1_1_5_3 lexicographically)
            # FastAPI JSON-encodes string responses, so use json() instead of text
            assert response.json() == "1_1_5_10"

