---
id: "retry_request"
sidebar_position: 8
title: "retry_request"
---

# ⚙️ retry_request

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`drive_service.py`](./drive_service.py) | **Line:** 519
:::

Execute API request with exponential backoff retry logic.

Attempts API request multiple times with increasing delays on
transient failures. Handles rate limits, timeouts, and server errors.

## Parameters

- **`request_func`** (Callable): Function to execute that returns API response. Should be parameterless lambda or closure wrapping the actual API call. Example: lambda: service.files().list().execute()
- **`operation_name`** (str, optional): Descriptive name for logging purposes. Helps identify which operation failed. Defaults to "operation".

## Returns

**Type**: `Any`

                all retries exhausted. Return type depends on API endpoint.

## Algorithm

- **Phase 1: Retry Loop**
  - 1. For attempt in range(max_retries):
  - 2. Attempt index: 0 to max_retries-1


- **Phase 2: Try Request Execution**
  - 1. Enter try block
  - 2. Call request_func() to execute API request
  - 3. If successful, return result immediately


- **Phase 3: Handle Errors**
  - 1. Catch TimeoutError, HttpError, or generic Exception
  - 2. Determine if error is retryable:
  - 3. TimeoutError: Always retryable
    - a. HttpError with status 429 (rate limit): Retryable
    - b. HttpError with status 500/503 (server error): Retryable
    - c. Other HttpError: Not retryable
  - 4. Other Exception: Retryable if not last attempt


- **Phase 4: Retry Decision**
  - 1. If should_retry AND not last attempt:
  - 2. Calculate delay: self.retry_delay * (2 ** attempt)
    - - Attempt 0: 1s, Attempt 1: 2s, Attempt 2: 4s, etc.
    - a. Print retry message with operation, attempt, delay
    - b. Sleep for calculated delay
    - c. Continue to next iteration
  - 3. If final attempt or non-retryable:
  - 4. Print final error message
    - a. Return None (failure)


- **Phase 5: Exhausted Retries**
  - 1. If loop completes without return
  - 2. Return None (all retries failed)

## Interactions

- **time.sleep()**: Implements backoff delay
- **googleapiclient.errors.HttpError**: HTTP error detection

## Example

```python
# Internal usage for API calls
def make_request():
    return self.service.files().list(q='...').execute()

result = drive._retry_request(make_request, "list_files")
if result:
    print("Success!")
else:
    print("Failed after retries")

# Handles rate limits automatically
# 429 error -> wait 1s -> retry
# 429 error -> wait 2s -> retry
# Success -> return result
```

## See Also

- `_execute_file_list_query()`: Uses this for queries
- `_execute_file_mutation()`: Uses this for mutations

## Notes

- Exponential backoff prevents request storms
- Rate limit (429) always retried
- Server errors (500, 503) retried
- Client errors (400, 404) not retried
- Timeout errors always retried
- Logs all retry attempts
- Returns None on final failure
- Max delay: retry_delay * (2 ** (max_retries - 1))
