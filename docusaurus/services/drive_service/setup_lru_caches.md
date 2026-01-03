---
id: "setup_lru_caches"
sidebar_position: 4
title: "setup_lru_caches"
---

# ⚙️ setup_lru_caches

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`drive_service.py`](./drive_service.py) | **Line:** 263
:::

Setup LRU (Least Recently Used) caches for frequent operations.

Creates a cached wrapper for get_file_info using functools.lru_cache
to provide an additional caching layer beyond the time-based cache.
This reduces API calls for frequently accessed file metadata.

## Returns

**Type**: `None`


## Algorithm

- **Phase 1: Define Cached Wrapper**
  - 1. Create inner function cached_get_file_info(file_id)
  - 2. Function calls self.get_file_info(file_id, use_cache=False)
  - 3. Bypasses time-based cache to avoid double-caching

- **Phase 2: Apply LRU Cache Decorator**
  - 1. Decorate function with @lru_cache(maxsize=128)
  - 2. Maintains 128 most recently accessed file IDs
  - 3. O(1) lookup performance for cached entries

- **Phase 3: Store Cached Function**
  - 1. Assign decorated function to self._cached_get_file_info
  - 2. Used by get_file_info when use_cache=True
  - 3. Provides fast access to frequently queried files

## Interactions

- **functools.lru_cache**: Provides LRU caching decorator
- **get_file_info()**: Wrapped method for file metadata

## Example

```python
# LRU cache used automatically
drive = DriveService(service)
info1 = drive.get_file_info('file_id')  # API call + cached
info2 = drive.get_file_info('file_id')  # LRU cache hit
# No API call for second request

# Cache cleared on invalidation
drive.create_folder('New Folder', parent_id='file_id')
info3 = drive.get_file_info('file_id')  # API call (cache cleared)
```

## See Also

- `get_file_info()`: Uses this cached wrapper
- `_invalidate_cache()`: Clears LRU cache
- `functools.lru_cache()`: Python LRU cache decorator

## Notes

- LRU cache size: 128 entries (configurable in code)
- Separate from time-based cache (complementary)
- Cleared on cache invalidation operations
- Provides O(1) lookup for hot files
- Automatically evicts least recently used entries
- Called automatically during __init__
