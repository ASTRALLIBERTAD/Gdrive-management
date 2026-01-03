---
id: "search_files"
sidebar_position: 11
title: "search_files"
---

# ⚙️ search_files

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`drive_service.py`](./drive_service.py) | **Line:** 841
:::

Search for files by name across Drive or within folder.

Searches for files matching the query text in their names.
Can search globally or within a specific folder.

## Parameters

- **`query_text`** (str): Text to search for in file names. Search is case-insensitive and matches partial names. Example: "assignment" matches "Assignment 1", "assignment.pdf", "Final_Assignment".
- **`folder_id`** (str, optional): Limit search to specific folder ID. If None, searches entire Drive. If provided, only searches within that folder. Defaults to None.
- **`use_cache`** (bool, optional): Whether to cache search results. Generally False for searches due to dynamic results. Set True for frequently repeated searches. Defaults to False.

## Returns

**Type**: `list`

                file contains: id, name, mimeType, modifiedTime, parents.
                Returns empty list [] if no matches or API failure.

## Algorithm

- **Phase 1: Generate Cache Key**:
  - 1. Format: "search_&#123;query_text&#125;_&#123;folder_id&#125;"
  - 2. Example: "search_assignment_None"

- **Phase 2: Check Cache** (if use_cache=True):
  - 1. Call self._get_cached(cache_key)
  - 2. If cached, return immediately

- **Phase 3: Build Search Query**:
  - 1. Base: "name contains '&#123;query_text&#125;' and trashed=false"
  - 2. If folder_id provided:
    - a. Append: " and '&#123;folder_id&#125;' in parents"
    - b. Limits search to folder

- **Phase 4: Execute Search**:
  - 1. Call _execute_file_list_query() with:
    - a. query: search criteria
    - b. page_size: 50 (smaller for searches)
    - c. fields: minimal set (id, name, mimeType, modifiedTime, parents)
  - 2. Returns API response or None

- **Phase 5: Extract Files**:
  - 1. If result is dict:
    - a. Extract files: result.get('files', [])
  - 2. If result is None:
    - a. files = [] (empty list)

- **Phase 6: Update Cache** (if use_cache and files found):
  - 1. Call _set_cache(cache_key, files)

- **Phase 7: Return Results**:
  - 1. Return files list (may be empty)

## Interactions

- **_get_cached()**: Checks cache
- **_execute_file_list_query()**: Executes search
- **_set_cache()**: Stores results if caching enabled

## Example

```python
# Search entire Drive
files = drive.search_files('homework')
print(f"Found {len(files)} files matching 'homework'")
for file in files:
    print(f"  - {file['name']}")

# Search within folder
files = drive.search_files('report', folder_id='folder_id')

# Cache frequently repeated searches
files = drive.search_files('template', use_cache=True)
```

## See Also

- `list_files()`: List folder contents
- `find_file()`: Find by exact name
- `_execute_file_list_query()`: Query execution

## Notes

- Search is case-insensitive
- Matches partial names (contains, not exact)
- Excludes trashed files automatically
- Returns empty list on no matches
- Caching disabled by default (dynamic results)
- Page size limited to 50 for searches
- Returns parents field for context
