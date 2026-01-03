---
id: "set_cache"
sidebar_position: 6
title: "set_cache"
---

# ⚙️ set_cache

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`drive_service.py`](./drive_service.py) | **Line:** 395
:::

Store data in cache with current timestamp.

Saves operation result in cache with timestamp for TTL validation.
Cache entries automatically expire based on age.

## Parameters

- **`key`** (str): Cache key for storage. Should be unique per operation and parameters. Format: "operation_param1_param2_...".
- **`data`** (Any): Data to cache. Typically dict or list from API responses. Must be serializable in memory.

## Returns

**Type**: `None`


## Algorithm

- **Phase 1: Create Cache Entry**:
  - 1. Get current timestamp: datetime.now()
  - 2. Create tuple: (data, timestamp)

- **Phase 2: Store in Cache**:
  - 1. Assign tuple to self._cache[key]
  - 2. Overwrites existing entry if present

## Interactions

- **datetime.now()**: Timestamp for TTL calculation

## Example

```python
# Internal usage after successful API call
result = self.service.files().list(...).execute()
self._set_cache('files_root_100_None', result)
# Data now available for cache_ttl seconds
```

## See Also

- `_get_cached()`: Retrieves cached data
- `_invalidate_cache()`: Clears cached data

## Notes

- Timestamp used for TTL validation
- Overwrites existing cache entries
- No size limit on cache (consider for large datasets)
- Data stored in memory (not persisted to disk)
