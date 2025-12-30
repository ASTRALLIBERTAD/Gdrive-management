---
id: "_start_polling"
sidebar_position: 9
title: "_start_polling"
---

# ⚙️ _start_polling

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`firebase_mobile_login.py`](./firebase_mobile_login.py) | **Line:** 875
:::

Initiate background polling for OAuth token retrieval.

Starts a daemon thread that periodically checks the callback server
for OAuth tokens matching the current session ID. Polls every 5
seconds for a maximum of 5 minutes (60 attempts). Handles token
receipt and timeout scenarios.

## Returns

**Type**: `None`

                callback server and invokes handlers based on results.

## Algorithm

- 1. **Set Polling Flag**:
    - a. Set self.polling = True
    - b. Indicates polling thread is active
    - c. Used to control loop continuation

  - 2. **Define Polling Function** (inner poll()):
    - a. Set max_attempts = 60 (5 minutes total)
    - b. Initialize attempt = 0 (counter)
    - c. Enter while loop: while polling AND attempt < max_attempts

    - d. **Update Status** (in loop):
    - - Call page.run_task(_update_waiting_status, attempt)
    - - Updates UI with animated dots on main thread
    - - Dots cycle: ".", "..", "..." based on attempt number

    - e. **Try Token Check**:
    - i. Construct check_url for callback server
    - Format: 'https://lms-callback.vercel.app/api/token/&#123;session_id&#125;'
    - ii. Create urllib.request.Request with check_url
    - iii. Add 'Accept: application/json' header
    - iv. Try to open URL with 10-second timeout
    - v. Read and decode response as UTF-8
    - vi. Parse JSON response with json.loads()
    - vii. Check if response has 'success' and 'token' fields
    - viii. If token.access_token exists:
    - - Call page.run_task(_handle_tokens, token_info)
    - - Runs token handler on main thread
    - - Return from poll() function (exit loop)
    - ix. If HTTPError (404 = token not ready yet):
    - - Pass (ignore, continue polling)
    - x. If other exception during token check:
    - - Pass (ignore, continue polling)

    - f. **Wait Between Attempts**:
    - i. Import time module
    - ii. Call time.sleep(5) to wait 5 seconds
    - iii. Increment attempt counter: attempt += 1

    - g. **Handle General Errors**:
    - i. Catch any exception in outer try block
    - ii. Sleep 5 seconds
    - iii. Increment attempt counter
    - iv. Continue polling (resilient to transient errors)

    - h. **Check Timeout** (after loop):
    - i. If attempt &gt;= max_attempts:
    - - Call page.run_task(_handle_timeout)
    - - Notifies user of timeout on main thread

  - 3. **Create Polling Thread**:
    - a. Instantiate threading.Thread
    - b. Set target to poll function (defined above)
    - c. Set daemon=True (thread exits when app exits)
    - d. Thread won't block application shutdown

  - 4. **Start Thread**:
    - a. Call thread.start()
    - b. Thread begins executing poll() in background
    - c. Main thread (UI) continues immediately
    - d. Polling runs asynchronously

## Interactions

- **threading.Thread**: Creates background polling thread
- **urllib.request**: Makes HTTP GET requests to callback server
- **json.loads()**: Parses JSON token responses
- **time.sleep()**: Waits between polling attempts
- **page.run_task()**: Schedules UI updates on main thread
- **_update_waiting_status()**: Updates status text with dots
- **_handle_tokens()**: Processes received OAuth tokens
- **_handle_timeout()**: Handles polling timeout

## Example

```python
# After handle_login() launches browser
login._start_polling()
# Polling thread starts in background

# Polling sequence (every 5 seconds):
# Attempt 1: Check callback server -> no token yet
# Status: "Waiting for sign-in."
# Attempt 2: Check callback server -> no token yet
# Status: "Waiting for sign-in.."
# Attempt 3: Check callback server -> no token yet
# Status: "Waiting for sign-in..."
# Attempt 4: Check callback server -> token found!
# Calls _handle_tokens(token_info)
# Polling stops

# If user never completes sign-in:
# After 60 attempts (5 minutes):
# Calls _handle_timeout()
# Status: "Timeout - Sign-in took too long"
```

## See Also

- `handle_login()`: Calls this to start polling
- `_update_waiting_status()`: Updates status with dots
- `_handle_tokens()`: Processes tokens when received
- `_handle_timeout()`: Handles timeout after 5 minutes
- `threading`: Thread-based parallelism

## Notes

- Polling runs for maximum 5 minutes (60 x 5 seconds)
- Daemon thread exits automatically when app closes
- HTTP 404 errors are expected (token not ready yet)
- All UI updates run on main thread via page.run_task()
- Transient network errors don't stop polling (resilient)
- Polling stops immediately when token received
- Callback server indexed by session_id for token lookup
- 10-second timeout per HTTP request prevents long hangs
- Status dots provide visual feedback that polling is active
