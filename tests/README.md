# Unit Tests

This directory contains unit tests for the API endpoints.

## Setup

Install the test dependencies:

```bash
pip install -r requirements.txt
```

## Running Tests

### Local Development

Run all tests:

```bash
pytest
```

Run tests with verbose output:

```bash
pytest -v
```

Run a specific test class:

```bash
pytest tests/test_routers.py::TestDownloadEndpoint
```

Run a specific test:

```bash
pytest tests/test_routers.py::TestDownloadEndpoint::test_download_file_success
```

### Running Tests in Docker

The tests are included in the Docker image. You can run them in several ways:

**Option 1: Using the helper script**

```bash
./run-tests.sh
```

**Option 2: Using docker-compose**

```bash
docker-compose run --rm app pytest
```

**Option 3: In a running container**

```bash
docker exec -it <container-name> pytest
```

**With specific options:**

```bash
# Verbose output
docker-compose run --rm app pytest -v

# Specific test
docker-compose run --rm app pytest tests/test_routers.py::TestDownloadEndpoint

# With coverage (if installed)
docker-compose run --rm app pytest --cov=app
```

## Test Coverage

The tests cover all three main endpoints:

1. **`/download`** - File download endpoint
   - Successful file download
   - File not found errors
   - SHA256 checksum calculation
   - Empty filename handling

2. **`/file_list/{folder}`** - Folder listing endpoint
   - Successful folder listing
   - Folder not found errors
   - Empty folder handling
   - Nested folder structures

3. **`/latest_version/{model_id}`** - Latest firmware version endpoint
   - Successful version retrieval
   - Model not found errors
   - Single version handling
   - Multiple models handling
   - Version ordering (numeric, not lexicographic)
   - Complex version numbers

## Test Structure

Tests use temporary directories to avoid modifying the actual firmware folder. Each test creates its own isolated environment and cleans up after execution.

