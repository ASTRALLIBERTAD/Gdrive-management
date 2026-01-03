---
id: "invalidate_cache"
sidebar_position: 7
title: "invalidate_cache"
---

# ⚙️ invalidate_cache

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`drive_service.py`](./drive_service.py) | **Line:** 440
:::

Clear cached data for specific folder or entire cache.

Removes cache entries to maintain consistency after mutations
(create, update, delete operations). Supports selective or
full cache invalidation.

## Parameters

- **`folder_id`** (str, optional): Specific folder ID to invalidate. Clears all cache entries containing this folder_id in key. If None, clears entire cache. Defaults to None.

## Returns

**Type**: `None`


## Algorithm

- **Phase 1: Check Invalidation Scope**
  - 1. If folder_id provided:
  - 2. Selective invalidation (folder-specific)
  - 3. If folder_id is None:
  - 4. Full invalidation (entire cache)


- **Phase 2: Selective Invalidation (if folder_id)**
  - 1. Find keys containing folder_id
  - 2. Create list: keys_to_remove = [k for k in cache if folder_id in k]
  - 3. Delete each matching key from cache
  - 4. Try to clear LRU cache:
  - 5. Check if _cached_get_file_info exists
    - a. Call cache_clear() on LRU cache
    - b. Catch and ignore errors (defensive)


- **Phase 3: Full Invalidation (if folder_id is None)**
  - 1. Call self._cache.clear()
  - 2. Removes all cache entries
  - 3. Clear LRU cache if exists:
  - 4. Call _cached_get_file_info.cache_clear()

## Interactions

- **dict.clear()**: Clears dictionary
- **lru_cache.cache_clear()**: Clears LRU cache

## Example

```python
# After creating file in folder
drive.create_folder('New Folder', parent_id='root')
drive._invalidate_cache('root')  # Clear root folder cache
# Next list_files('root') will hit API

# After major changes, clear all
drive._invalidate_cache()  # Clear entire cache
```

## See Also

- `_execute_file_mutation()`: Calls this after mutations
- `create_folder()`: Triggers invalidation
- `delete_file()`: Triggers invalidation

## Notes

- Called automatically after mutations
- Selective invalidation more efficient
- Full invalidation after major operations
- LRU cache cleared defensively (catches errors)
- Maintains cache consistency with Drive state
