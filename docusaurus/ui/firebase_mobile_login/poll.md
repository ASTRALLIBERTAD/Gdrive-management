---
id: "poll"
sidebar_position: 12
title: "poll"
---

# ⚙️ poll

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`firebase_mobile_login.py`](./firebase_mobile_login.py) | **Line:** 1287
:::

Handle polling timeout when authentication takes too long.

Asynchronous method that resets UI state and displays a timeout
message when the maximum polling duration (5 minutes) is exceeded
without receiving OAuth tokens. Allows user to retry login.

## Returns

**Type**: `None`


## Algorithm

- 1. **Stop Polling**:
    - a. Set self.polling = False
    - b. Ensures polling loop exits (if not already exited)
    - c. Prevents further callback server checks

  - 2. **Update Status Message**:
    - a. Call update_status with timeout message
    - b. Message: "Timeout - Sign-in took too long"
    - c. Color: ft.Colors.ORANGE (warning color)
    - d. Indicates user action needed (retry)

  - 3. **Re-enable Login Button**:
    - a. Set self.login_button.disabled = False
    - b. Allows user to click button again
    - c. Enables retry of authentication flow

  - 4. **Hide Progress Indicator**:
    - a. Set self.progress.visible = False
    - b. Removes spinning progress ring
    - c. Indicates process is no longer active

  - 5. **Refresh UI**:
    - a. Call self.page.update()
    - b. Applies all UI state changes
    - c. User sees updated status, enabled button, no spinner

## Interactions

- **update_status()**: Shows timeout message to user
- **ft.Page.update()**: Renders UI changes

## Example

```python
# After 60 polling attempts (5 minutes) without token
await login._handle_timeout()
# Status: "Timeout - Sign-in took too long" (orange)
# Login button: enabled (can retry)
# Progress indicator: hidden

# User can now click "Sign in with Google" again
# This starts a new session with fresh session_id
```

## See Also

- `_start_polling()`: Calls this after max polling attempts
- `handle_login()`: User clicks button to retry

## Notes

- Timeout occurs after 60 attempts x 5 seconds = 5 minutes
- Must be called via page.run_task() from polling thread
- Async method for Flet async UI updates
- Orange color suggests recoverable issue (not error)
- Possible timeout causes:
- User didn't complete sign-in in browser
- User closed browser before completing
- Network issues preventing callback server access
- Callback server issues storing/retrieving tokens
- User can retry immediately (no waiting period)
- New retry generates new session_id for fresh attempt
- No cleanup needed (polling already stopped)
