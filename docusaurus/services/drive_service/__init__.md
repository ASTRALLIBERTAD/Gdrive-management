---
id: "__init__"
sidebar_position: 3
title: "__init__"
---

# 🔧 __init__

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`drive_service.py`](./drive_service.py) | **Line:** 184
:::

Initialize DriveService with API service and configuration.

Sets up the Drive service wrapper with caching, retry parameters,
and LRU cache initialization for optimized API operations.

## Parameters

- **`service`** (googleapiclient.discovery.Resource): Authenticated Google Drive API v3 service object obtained from GoogleAuth.get_service(). Must be properly authenticated with Drive API scope.
- **`cache_ttl`** (int, optional): Cache time-to-live in seconds. Cached data expires after this duration. Longer TTL reduces API calls but may serve stale data. Shorter TTL ensures freshness but increases API usage. Defaults to 300 (5 minutes).
- **`max_retries`** (int, optional): Maximum number of retry attempts for transient failures (rate limits, server errors). Each retry uses exponential backoff. Higher values improve reliability but increase latency on failures. Defaults to 3.

## Algorithm

- **Phase 1: Store Service Reference**
  - 1. Assign service parameter to self.service
  - 2. Service provides access to all Drive API endpoints


- **Phase 2: Initialize Cache System**
  - 1. Create empty cache dictionary: self._cache = &#123;&#125;
  - 2. Store TTL value: self._cache_ttl = cache_ttl
  - 3. Cache stores (data, timestamp) tuples


- **Phase 3: Configure Retry Parameters**
  - 1. Set max_retries: self.max_retries = max_retries
  - 2. Set base retry delay: self.retry_delay = 1 second
  - 3. Actual delay uses exponential backoff: delay * (2 ** attempt)

- **Phase 4: Setup LRU Caches**
  - 1. Call self._setup_lru_caches()
  - 2. Creates cached wrapper for get_file_info
  - 3. LRU cache maxsize: 128 entries

## Interactions

- **googleapiclient.discovery.Resource**: Drive API service
- **_setup_lru_caches()**: Initializes LRU cached methods

## Example

```python
# Initialize with default settings
auth = GoogleAuth()
service = auth.get_service()
drive = DriveService(service)

# Custom cache TTL (10 minutes)
drive = DriveService(service, cache_ttl=600)

# More aggressive retries
drive = DriveService(service, max_retries=5)

# Short cache for frequently changing data
drive = DriveService(service, cache_ttl=60, max_retries=3)
```

## See Also

- `_setup_lru_caches()`: Initializes LRU caching
- `GoogleAuth`: Provides service

## Notes

- service must be authenticated with Drive API scope
- cache_ttl of 0 effectively disables caching
- max_retries of 1 means no retries (single attempt only)
- LRU cache initialized automatically
- Cache starts empty (populated on first requests)
