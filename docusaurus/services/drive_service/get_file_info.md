---
id: "get_file_info"
sidebar_position: 12
title: "get_file_info"
---

# ⚙️ get_file_info

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`drive_service.py`](./drive_service.py) | **Line:** 948
:::

Get detailed metadata for a specific file or folder.

Retrieves comprehensive information about a file including name,
type, size, timestamps, owners, and links. Uses LRU cache for
frequently accessed files.

## Parameters

- **`file_id`** (str): Google Drive file or folder ID. Format: 33-character alphanumeric string. Example: "1abc...xyz".
- **`use_cache`** (bool, optional): Whether to use cached info. If True, checks LRU cache and time-based cache before API call. If False, always queries API. Defaults to True.

## Returns

**Type**: `dict or None`

                - id (str): File ID
                - name (str): File/folder name
                - mimeType (str): MIME type (e.g., 'application/pdf')
                - size (str, optional): Size in bytes (not present for folders)
                - createdTime (str): ISO 8601 creation timestamp
                - modifiedTime (str): ISO 8601 modification timestamp
                - owners (list): List of owner objects with displayName, emailAddress
                - parents (list): List of parent folder IDs
                - webViewLink (str): URL to view file in browser
                Returns None if file not found or API error.

## Algorithm

- **Phase 1: Try LRU Cache (if use_cache=True)**
  - 1. Check if _cached_get_file_info exists
  - 2. Try calling _cached_get_file_info(file_id)
  - 3. If successful, return cached result
  - 4. If exception, continue to next step


- **Phase 2: Generate Cache Key**
  - 1. Format: "fileinfo_&#123;file_id&#125;"
  - 2. Example: "fileinfo_1abc...xyz"


- **Phase 3: Check Time-Based Cache (if use_cache=True)**
  - 1. Call self._get_cached(cache_key)
  - 2. If cached and not expired, return data


- **Phase 4: Define Request Function**
  - 1. Create make_request() closure
  - 2. Calls service.files().get() with:
  - 3. fileId=file_id
    - a. fields: comprehensive field list
  - 4. Returns file metadata dictionary


- **Phase 5: Execute with Retry**
  - 1. Call _retry_request(make_request, operation_name)
  - 2. Returns file dict or None on failure


- **Phase 6: Update Cache (if result not None)**
  - 1. Call _set_cache(cache_key, file)
  - 2. Stores with current timestamp


- **Phase 7: Return Result**
  - 1. Return file dictionary or None

## Interactions

- **_cached_get_file_info**: LRU cached wrapper
- **_get_cached()**: Time-based cache check
- **service.files().get()**: Drive API endpoint
- **_retry_request()**: Retry wrapper
- **_set_cache()**: Stores result

## Example

```python
# Get file info
info = drive.get_file_info('file_abc123')
print(f"Name: {info['name']}")
print(f"Type: {info['mimeType']}")
print(f"Size: {info.get('size', 'N/A')} bytes")
print(f"Modified: {info['modifiedTime']}")
print(f"Owner: {info['owners'][0]['displayName']}")

# Get folder info
folder = drive.get_file_info('folder_xyz')
is_folder = folder['mimeType'] == 'application/vnd.google-apps.folder'

# Bypass cache for fresh data
info = drive.get_file_info('file_id', use_cache=False)

# Handle not found
info = drive.get_file_info('invalid_id')
if info:
    print("File exists")
    else:
    print("File not found")
```

## See Also

- `_setup_lru_caches()`: LRU cache initialization
- `resolve_drive_link()`: Parse URL and get info
- `list_files()`: List folder contents

## Notes

- Uses dual caching (LRU + time-based)
- LRU cache maxsize: 128 entries
- Time cache TTL: cache_ttl seconds
- Size field absent for folders
- Returns None for non-existent files
- webViewLink for browser viewing
- Comprehensive field set for all metadata
