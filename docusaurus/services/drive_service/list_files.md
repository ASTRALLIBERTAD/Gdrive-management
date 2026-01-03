---
id: "list_files"
sidebar_position: 10
title: "list_files"
---

# ⚙️ list_files

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`drive_service.py`](./drive_service.py) | **Line:** 718
:::

List files and folders in a Drive folder with caching.

Retrieves contents of a specified folder with automatic caching
to reduce API calls. Supports pagination for large folders.

## Parameters

- **`folder_id`** (str, optional): Google Drive folder ID to list contents. Use 'root' for root folder, or specific folder ID. Defaults to 'root'.
- **`page_size`** (int, optional): Maximum number of results per page. Range: 1-1000. Recommended: 100-500 for balance of performance and response size. Defaults to 100.
- **`page_token`** (str, optional): Pagination token from previous response for fetching subsequent pages. Use result['nextPageToken'] from previous call. None for first page. Defaults to None.
- **`use_cache`** (bool, optional): Whether to use cached results. If True, checks cache before API call. If False, always queries API and updates cache. Defaults to True.

## Returns

**Type**: `dict or None`

                - files (list): List of file/folder objects with metadata
                - nextPageToken (str or None): Token for next page, None if last page
                Returns None if API request fails after retries.

## Algorithm

- **Phase 1: Generate Cache Key**:
  - 1. Format: "files_&#123;folder_id&#125;_&#123;page_size&#125;_&#123;page_token&#125;"
  - 2. Example: "files_root_100_None"

- **Phase 2: Check Cache** (if use_cache=True):
  - 1. Call self._get_cached(cache_key)
  - 2. If cached data exists and not expired:
    - a. Print cache hit message
    - b. Return cached data immediately

- **Phase 3: Build Query**:
  - 1. Format: "'&#123;folder_id&#125;' in parents and trashed=false"
  - 2. Filters: folder contains file, not in trash

- **Phase 4: Execute API Request**:
  - 1. Call _execute_file_list_query() with query and parameters
  - 2. Returns raw API response or None

- **Phase 5: Process Response**:
  - 1. If result is None:
    - a. API call failed
    - b. Return None
  - 2. If result is dict:
    - a. Extract 'files' list (empty list if missing)
    - b. Extract 'nextPageToken' (None if last page)
    - c. Create formatted_result dict

- **Phase 6: Update Cache**:
  - 1. Call _set_cache(cache_key, formatted_result)
  - 2. Stores result with current timestamp

- **Phase 7: Return Result**:
  - 1. Return formatted_result dictionary

## Interactions

- **_get_cached()**: Checks cache
- **_execute_file_list_query()**: Executes API request
- **_set_cache()**: Stores result

## Example

```python
# List root folder
result = drive.list_files('root')
for file in result['files']:
    print(f"{file['name']} - {file['mimeType']}")

# List specific folder
result = drive.list_files('folder_abc123')

# Pagination
result = drive.list_files('root', page_size=50)
all_files = result['files']
while result.get('nextPageToken'):
    result = drive.list_files(
    'root',
    page_size=50,
    page_token=result['nextPageToken']
    )
    all_files.extend(result['files'])

# Bypass cache
result = drive.list_files('root', use_cache=False)
```

## See Also

- `search_files()`: Search across folders
- `get_folder_tree()`: Recursive folder structure
- `_execute_file_list_query()`: Query execution

## Notes

- Cached for cache_ttl seconds (default 300s)
- Cache invalidated on folder mutations
- Excludes trashed files automatically
- Results sorted by folder then name
- Returns None on API failure
- Empty folder returns &#123;'files': [], 'nextPageToken': None&#125;
