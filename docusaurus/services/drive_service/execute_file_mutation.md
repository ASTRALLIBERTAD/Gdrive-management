---
id: "execute_file_mutation"
sidebar_position: 14
title: "execute_file_mutation"
---

# ⚙️ execute_file_mutation

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`drive_service.py`](./drive_service.py) | **Line:** 1180
:::

Execute file mutation operation with retry and cache invalidation.

Wrapper for write operations (create, update, delete) that handles
retry logic and automatic cache invalidation to maintain consistency.

## Parameters

- **`operation_name`** (str): Descriptive name for logging. Example: "create_folder(New Folder)".
- **`request_func`** (Callable): Function performing the mutation. Should return API response dict. Example: lambda: service.files().create(...).execute()
- **`parent_id`** (str, optional): Parent folder ID affected by mutation. Used for cache invalidation. If None, no cache invalidation performed. Defaults to None.

## Returns

**Type**: `Any`

                Return type depends on operation (typically dict).

## Algorithm

- **Phase 1: Execute with Retry**
  - 1. Call _retry_request(request_func, operation_name)
  - 2. Returns result or None on failure


- **Phase 2: Invalidate Cache (if successful and parent_id)**
  - 1. If result is not None AND parent_id provided:
  - 2. Call _invalidate_cache(parent_id)
    - a. Clears cache entries for affected folder
    - b. Maintains consistency with Drive state


- **Phase 3: Return Result**
  - 1. Return result (success) or None (failure)

## Interactions

- **_retry_request()**: Retry wrapper
- **_invalidate_cache()**: Cache management

## Example

```python
# Internal usage for mutations
def make_request():
    return self.service.files().create(
    body={'name': 'New File', 'parents': ['root']},
    fields='id, name'
    ).execute()

result = drive._execute_file_mutation(
    'create_file(New File)',
    make_request,
    parent_id='root'
    )
# Cache for 'root' now invalidated
```

## See Also

- `create_folder()`: Uses this for creation
- `_retry_request()`: Retry logic
- `_invalidate_cache()`: Cache management

## Notes

- Automatically retries on transient failures
- Invalidates cache only on success
- parent_id optional but recommended
- Returns None on failure (caller should check)
- Maintains cache consistency
