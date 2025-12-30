---
id: "handle_error"
sidebar_position: 8
title: "handle_error"
---

# ⚙️ handle_error

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`login.py`](./login.py) | **Line:** 623
:::

Display error message and log detailed error information.

Handles authentication errors by updating the UI with a user-friendly
error message, re-enabling the login button for retry, and logging
detailed error information to the console for debugging. Truncates
long error messages for UI display.

## Parameters

- **`error`** (Exception): The exception that occurred during authentication. Can be any Exception subclass (ValueError, ConnectionError, etc.). Error message extracted via str(error).
- **`context`** (str, optional): Context description for error logging and display. Prepended to error message. Examples: "Login", "Desktop login", "Browser launch". Defaults to "Login".

## Returns

**Type**: `None`


## Algorithm

- 1. **Extract Error Message**:
    - a. Convert error to string: str(error)
    - b. Store in error_msg variable
    - c. Full message preserved for logging

  - 2. **Update UI with Error**:
    - a. Truncate error_msg to first 50 characters
    - b. Append "..." if truncated
    - c. Format message: "&#123;context&#125; failed: &#123;error_msg[:50]&#125;..."
    - d. Call update_status() with:
    - i. Formatted error message
    - ii. Color: ft.Colors.RED_600 (error indication)
    - iii. disable_button: False (re-enable for retry)
    - e. User sees error message and enabled button

  - 3. **Log Detailed Error**:
    - a. Format console message: "&#123;context&#125; error: &#123;error&#125;"
    - b. Get full stack trace: traceback.format_exc()
    - c. Print formatted message with full traceback
    - d. Includes exception type, message, and call stack
    - e. Available in console for debugging

## Interactions

- **update_status()**: Shows error message to user
- **traceback.format_exc()**: Gets full exception traceback
- **str()**: Converts exception to string message

## Example

```python
# Network error during authentication
try:
    perform_oauth_request()
    except ConnectionError as e:
    login.handle_error(e, "Desktop login")
# Status: "Desktop login failed: Failed to connect..." (red)
# Button: enabled (user can retry)
# Console: "Desktop login error: Failed to connect to server"
#          "Traceback (most recent call last):"
#          "  File '...', line ..., in perform_oauth_request"
#          "ConnectionError: Failed to connect to server"

# Generic error with long message
try:
    auth.login()
    except ValueError as e:
    login.handle_error(e, "Login")
# Status: "Login failed: The authentication token is inval..." (red)
```

## See Also

- `update_status()`: Updates status message and button
- `handle_success()`: Handles successful authentication
- `traceback`: Python traceback module for error logging

## Notes

- Error message truncated to 50 chars for UI display
- Full error logged to console for debugging
- Login button re-enabled to allow retry
- Red color clearly indicates error state
- Stack trace helps developers diagnose issues
- Context parameter helps identify error source
- Safe for any Exception subclass
