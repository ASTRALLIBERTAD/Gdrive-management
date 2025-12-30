---
id: "handle_login"
sidebar_position: 7
title: "handle_login"
---

# ⚙️ handle_login

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`firebase_mobile_login.py`](./firebase_mobile_login.py) | **Line:** 636
:::

Initiate the OAuth 2.0 authentication flow.

Handles the login button click by generating a secure session ID,
constructing the OAuth URL, launching the external browser, and
starting background token polling. Manages UI state throughout
the process with status updates and button state changes.

## Parameters

- **`e`** (ft.ControlEvent): Flet control event from login button click. Contains event source and metadata. Not used in logic but required by Flet event handler signature.

## Returns

**Type**: `None`

                - Generates and stores session_id
                - Updates UI status messages
                - Disables login button
                - Shows progress indicator
                - Launches external browser
                - Starts background polling thread

## Exceptions

Exception: Any exception during OAuth URL construction or browser
                launch is caught and displayed to user via status message.
                Login button re-enabled to allow retry.

## Algorithm

- 1. **Generate Session ID**:
    - a. Call secrets.token_urlsafe(16)
    - b. Generates 16-byte random token, base64url-encoded
    - c. Store in self.session_id (used as OAuth state parameter)
    - d. Provides CSRF protection and callback server lookup key

  - 2. **Update Initial Status**:
    - a. Call update_status("Opening browser...", ORANGE)
    - b. Indicates action in progress
    - c. Orange color suggests transitional state

  - 3. **Disable Login Button**:
    - a. Set self.login_button.disabled = True
    - b. Prevents double-click / multiple sessions
    - c. Button grayed out visually

  - 4. **Show Progress Indicator**:
    - a. Set self.progress.visible = True
    - b. Displays circular spinner
    - c. Provides visual feedback of active process

  - 5. **Refresh UI**:
    - a. Call self.page.update()
    - b. Apply button and progress changes immediately

  - 6. **Try OAuth Flow**:
    - a. Enter try block for error handling
    - b. Call _build_oauth_url() to construct auth URL
    - c. URL includes client_id, scopes, redirect_uri, state=session_id
    - d. Store result in oauth_url variable

  - 7. **Launch Browser**:
    - a. Call self.page.launch_url(oauth_url)
    - b. Opens system browser to Google OAuth page
    - c. User sees Google sign-in interface
    - d. Non-blocking operation (returns immediately)

  - 8. **Update Waiting Status**:
    - a. Call update_status("Waiting for sign-in...", BLUE_600)
    - b. Indicates waiting for user action in browser
    - c. Blue color suggests informational state
    - d. Call page.update() to apply change

  - 9. **Start Polling**:
    - a. Call _start_polling()
    - b. Launches background thread to check for tokens
    - c. Polls callback server every 5 seconds
    - d. Thread runs independently of UI

  - 10. **Handle Errors**:
    - a. Catch any Exception during OAuth flow
    - b. Import traceback module for detailed error info
    - c. Call update_status with error message (first 50 chars)
    - d. Set status color to RED_600 (error indication)
    - e. Re-enable login button: disabled = False
    - f. Hide progress indicator: visible = False
    - g. Print full error and traceback to console for debugging
    - h. User can retry login after error

## Interactions

- **secrets.token_urlsafe()**: Generates secure session ID
- **update_status()**: Shows progress messages to user
- **_build_oauth_url()**: Constructs OAuth authorization URL
- **ft.Page.launch_url()**: Opens external browser
- **_start_polling()**: Starts background token retrieval

## Example

```python
# User clicks login button
login.handle_login(click_event)
# Output sequence:
# 1. Status: "Opening browser..." (orange)
# 2. Button disabled, progress shown
# 3. Browser launches to accounts.google.com
# 4. Status: "Waiting for sign-in..." (blue)
# 5. Polling thread starts in background

# If error occurs (e.g., network failure)
# Status: "Error: Failed to connect..." (red)
# Button re-enabled, progress hidden
# User can click to retry
```

## See Also

- `_build_oauth_url()`: Constructs OAuth URL
- `_start_polling()`: Starts token polling thread
- `update_status()`: Updates status messages
- `_handle_tokens()`: Called when tokens received

## Notes

- Session ID provides CSRF protection via state parameter
- Login button disabled to prevent multiple concurrent sessions
- Progress indicator provides visual feedback during wait
- Browser launch is non-blocking (immediate return)
- Polling thread is daemon (won't block app exit)
- Error messages truncated to 50 chars for UI display
- Full errors printed to console for debugging
- User can retry login after error by clicking button again
