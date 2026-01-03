---
id: "driveservice"
sidebar_position: 2
title: "DriveService"
---

# 📦 DriveService

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-20%25-red)

:::info Source
**File:** [`drive_service.py`](./drive_service.py) | **Line:** 29
:::

High-level Google Drive API wrapper with caching and retry mechanisms.

DriveService provides an optimized interface to Google Drive API operations,
implementing intelligent caching, automatic retry with exponential backoff,
and comprehensive error handling. It abstracts low-level API complexity while
maintaining performance through LRU caching and request batching strategies.
This service layer sits between the raw Drive API and application logic,
managing cache invalidation, pagination, and transient failure recovery
automatically. It reduces API quota usage through strategic caching and
improves reliability through retry logic for rate limits and server errors.

## Purpose

- Provide high-level interface to Google Drive API operations
        - Implement intelligent caching with TTL (time-to-live)
        - Handle automatic retry with exponential backoff
        - Manage cache invalidation on mutations
        - Abstract pagination and API field specifications
        - Reduce API quota consumption through caching
        - Improve reliability with error recovery

## Attributes

- **`service`** (googleapiclient.discovery.Resource): Authenticated Google Drive API v3 service object from GoogleAuth. Provides access to all Drive API endpoints (files, about, permissions, etc.).
- **`max_retries`** (int): Maximum number of retry attempts for failed requests. Applied to transient errors (429, 500, 503 HTTP codes). Default: 3.
- **`retry_delay`** (int): Base delay in seconds for exponential backoff. Actual delay: retry_delay * (2 ** attempt). Default: 1 second.
- **`_cache`** (dict): Internal cache dictionary storing (data, timestamp) tuples. Keys are operation-specific strings. Cleared on invalidation.
- **`_cache_ttl`** (int): Cache time-to-live in seconds. Cached data expires after this duration. Default: 300 seconds (5 minutes).
- **`_cached_get_file_info`** (Callable): LRU-cached wrapper for get_file_info. Maxsize: 128 entries. Provides additional caching layer for frequently accessed file metadata.

## Algorithm

- **Phase 1: Initialization**
  - 1. Store authenticated Drive API service
  - 2. Initialize cache dictionary and TTL settings
  - 3. Configure retry parameters (max attempts, base delay)
  - 4. Setup LRU caches for file info operations

- **Phase 2: Read Operations** (list, search, get)
  - 1. Generate cache key from operation parameters
  - 2. Check cache for unexpired data
  - 3. If cache hit, return cached data immediately
  - 4. If cache miss, execute API request with retry
  - 5. Store successful result in cache with timestamp
  - 6. Return result to caller

- **Phase 3: Write Operations** (create, upload, update, delete)
  - 1. Execute mutation with retry logic
  - 2. On success, invalidate affected cache entries
  - 3. Invalidate parent folder caches
  - 4. Clear related LRU cache entries
  - 5. Return operation result

- **Phase 4: Retry Logic** (automatic on failures)
  - 1. Attempt API request
  - 2. On transient error (429, 500, 503, timeout):
    - a. Calculate delay: base * (2 ** attempt)
    - b. Sleep for calculated delay
    - c. Retry request
  - 3. On permanent error or max retries:
    - a. Log error
    - b. Return None or appropriate failure value

- **Phase 5: Cache Management**
  - 1. Cache entries include timestamp
  - 2. On read, check if timestamp + TTL > now
  - 3. If expired, delete entry and treat as cache miss
  - 4. On mutation, invalidate specific folder or all caches
  - 5. LRU cache cleared on invalidation

## Interactions

- **googleapiclient.discovery.Resource**: Drive API service from GoogleAuth
- **googleapiclient.errors.HttpError**: HTTP error handling
- **googleapiclient.http.MediaFileUpload**: File upload handling
- **googleapiclient.http.MediaIoBaseDownload**: File download handling
- **functools.lru_cache**: LRU caching decorator
- **utils.common.extract_drive_id**: URL parsing utility
- **utils.common.format_file_size**: Size formatting utility

## Example

```python
# Initialize with authenticated service
from services.auth_service import GoogleAuth
auth = GoogleAuth()
auth.login_desktop()
drive = DriveService(auth.get_service())

# List files in root folder
result = drive.list_files('root')
for file in result['files']:
    print(f"{file['name']} ({file['mimeType']})")

# Search for files
files = drive.search_files('assignment', folder_id='root')
print(f"Found {len(files)} matching files")

# Upload file with progress callback
def show_progress(current, total):
    print(f"Upload: {current}/{total} bytes")
result = drive.upload_file(
    'document.pdf',
    parent_id='folder_id',
    progress_callback=show_progress
    )

# Create folder
folder = drive.create_folder('New Folder', parent_id='root')
print(f"Created folder: {folder['id']}")

# Get file info (uses LRU cache)
info = drive.get_file_info('file_id')
print(f"File: {info['name']}, Size: {info.get('size', 'N/A')}")

# Move file
drive.move_file('file_id', 'new_folder_id')

# Delete file
success = drive.delete_file('file_id')
```

## See Also

- `GoogleAuth`: Provides authenticated service
- `Dashboard`: Primary consumer of DriveService
- `extract_drive_id()`: URL parsing utility
- `Drive API Reference <[https://developers.google.com/drive/api/v3/reference>`_](https://developers.google.com/drive/api/v3/reference>`_)

## Notes

- Cache automatically expires after TTL (default 5 minutes)
- Retry logic handles rate limits (429) and server errors (500, 503)
- Exponential backoff prevents request storms
- LRU cache maxsize 128 for file info operations
- Cache invalidation on mutations maintains consistency
- Pagination handled automatically with nextPageToken
- Field specifications optimize API response size
- Resumable uploads supported for large files
- Progress callbacks available for uploads

## References

- Google Drive API v3: [https://developers.google.com/drive/api/v3/reference](https://developers.google.com/drive/api/v3/reference)
- Exponential Backoff: [https://cloud.google.com/storage/docs/retry-strategy](https://cloud.google.com/storage/docs/retry-strategy)
- LRU Cache: [https://docs.python.org/3/library/functools.html#functools.lru_cache](https://docs.python.org/3/library/functools.html#functools.lru_cache)
