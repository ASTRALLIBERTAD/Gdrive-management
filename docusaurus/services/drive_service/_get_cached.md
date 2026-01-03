---
id: "_get_cached"
sidebar_position: 5
title: "_get_cached"
---

# ⚙️ _get_cached

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`drive_service.py`](./drive_service.py) | **Line:** 323
:::

Retrieve data from time-based cache if not expired.

Checks if cached data exists and is still valid based on TTL
(time-to-live). Automatically removes expired entries.

## Parameters

- **`key`** (str): Cache key to lookup. Typically formatted as operation_parameter format (e.g., "files_root_100_None").

## Returns

**Type**: `Any`

                or expired. Return type matches cached data type (typically
                dict or list for Drive operations).

## Algorithm

- **Phase 1: Check Key Existence**
  - 1. If key in self._cache dictionary:
  - 2. Proceed to validation
  - 3. If key not in cache:
  - 4. Return None (cache miss)


- **Phase 2: Extract Cache Entry**
  - 1. Get tuple from cache: (data, timestamp)
  - 2. data: The cached response data
  - 3. timestamp: datetime when cached


- **Phase 3: Validate Timestamp**
  - 1. Calculate age: datetime.now() - timestamp
  - 2. Compare age to self._cache_ttl
  - 3. If age < cache_ttl:
  - 4. Data still valid
    - a. Return data
  - 5. If age &gt;= cache_ttl:
  - 6. Data expired
    - a. Delete cache entry
    - b. Return None (expired)

## Interactions

- **datetime.now()**: Gets current timestamp
- **timedelta**: Calculates time differences

## Example

```python
# Internal usage by public methods
cached = drive._get_cached('files_root_100_None')
if cached:
    print("Cache hit!")
    return cached
    else:
    print("Cache miss, calling API...")
```

## See Also

- `_set_cache()`: Stores data in cache
- `_invalidate_cache()`: Clears cache entries

## Notes

- Automatically removes expired entries
- TTL set during initialization (default 300s)
- Returns None for both miss and expiration
- Cache keys are operation-specific strings
- Expired entries deleted to free memory
