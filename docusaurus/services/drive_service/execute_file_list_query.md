---
id: "execute_file_list_query"
sidebar_position: 9
title: "execute_file_list_query"
---

# ⚙️ execute_file_list_query

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`drive_service.py`](./drive_service.py) | **Line:** 629
:::

Execute Drive API files.list query with retry logic.

Wrapper for files().list() API endpoint with configurable parameters
and automatic retry handling. Used by list and search operations.

## Parameters

- **`query`** (str): Drive API query string in Drive query language. Example: "'root' in parents and trashed=false". See Drive API docs for query syntax.
- **`page_size`** (int, optional): Number of results per page. Maximum 1000, recommended 100-500 for performance. Defaults to 100.
- **`page_token`** (str, optional): Pagination token from previous response. Use nextPageToken for subsequent pages. None for first page. Defaults to None.
- **`fields`** (str, optional): API fields to return in response. Reduces payload size. Format: "nextPageToken, files(field1, field2, ...)". Defaults to standard file fields.
- **`order_by`** (str, optional): Sort order for results. Format: "field1,field2" or "field1 desc". Common: "folder,name", "modifiedTime desc". Defaults to "folder,name".

## Returns

**Type**: `dict or None`

                'nextPageToken' for pagination. None if request fails after
                all retries. Structure: &#123;'files': [...], 'nextPageToken': '...'&#125;.

## Algorithm

- **Phase 1: Define Request Function**:
  - 1. Create make_request() closure
  - 2. Calls self.service.files().list() with parameters:
    - a. q=query (filter condition)
    - b. pageSize=page_size (results per page)
    - c. pageToken=page_token (pagination)
    - d. fields=fields (response fields)
    - e. orderBy=order_by (sort order)
  - 2. Calls .execute() to perform request
  - 3. Returns API response dictionary

- **Phase 2: Execute with Retry**:
  - 1. Call self._retry_request(make_request, operation_name)
  - 2. operation_name includes truncated query for logging
  - 3. Returns result or None on failure

## Interactions

- **service.files().list()**: Drive API list endpoint
- **_retry_request()**: Retry wrapper with backoff

## Example

```python
# List files in folder
query = "'root' in parents and trashed=false"
result = drive._execute_file_list_query(query, page_size=50)
print(f"Found {len(result['files'])} files")

# Search for PDFs
query = "mimeType='application/pdf' and trashed=false"
result = drive._execute_file_list_query(query)

# Pagination
result = drive._execute_file_list_query(query, page_size=100)
while result and result.get('nextPageToken'):
    result = drive._execute_file_list_query(
    query,
    page_token=result['nextPageToken']
    )
```

## See Also

- `list_files()`: Public method using this
- `search_files()`: Search using this
- `_retry_request()`: Retry wrapper

## Notes

- Truncates query in logs (first 50 chars)
- Fields optimization reduces bandwidth
- order_by: folders before files by default
- page_size max 1000 (API limit)
- Returns None on failure (caller should check)
