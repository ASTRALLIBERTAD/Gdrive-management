---
id: "_handle_desktop_login"
sidebar_position: 13
title: "_handle_desktop_login"
---

# ⚙️ _handle_desktop_login

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`login.py`](./login.py) | **Line:** 1041
:::

Execute desktop OAuth flow with local callback server.

Performs OAuth 2.0 authentication on desktop platforms using a
temporary local HTTP server to handle the OAuth callback. Opens
the system browser for user authentication and waits for the
callback with authorization code.

## Returns

**Type**: `None`


## Algorithm

- 1. **Update UI for Processing**:
    - a. Call update_status() with message
    - b. Message: "Opening browser for authentication..."
    - c. Color: default (blue)
    - d. disable_button: True (prevents double-click)

  - 2. **Try Desktop Authentication**:
    - a. Enter try block for error handling
    - b. Call self.auth.login_desktop()
    - c. Auth service performs:
    - i. Start local HTTP server on available port
    - ii. Build OAuth URL with redirect to localhost
    - iii. Open system browser to OAuth URL
    - iv. Wait for user to authenticate
    - v. Receive callback with authorization code
    - vi. Exchange code for access token
    - vii. Store credentials in auth service
    - d. login_desktop() method blocks until complete or timeout

  - 3. **Check Authentication Result**:
    - a. Call self.auth.is_authenticated()
    - b. Returns True if credentials valid and stored
    - c. If True (authenticated):
    - i. Call self.handle_success()
    - ii. Shows success message (green)
    - iii. Invokes on_success callback
    - iv. Typically navigates to dashboard
    - d. If False (not authenticated):
    - i. Call update_status() with error message
    - ii. Message: "Login completed but authentication failed"
    - iii. Color: RED_600 (error indication)
    - iv. disable_button: False (re-enable for retry)

  - 4. **Handle Exceptions**:
    - a. Catch any Exception during authentication
    - b. Examples: NetworkError, TimeoutError, ValueError
    - c. Call self.handle_error(ex, "Desktop login")
    - d. handle_error displays user message and logs details

## Interactions

- **update_status()**: Shows progress and results
- **GoogleAuth.login_desktop()**: Executes OAuth flow
- **GoogleAuth.is_authenticated()**: Validates credentials
- **handle_success()**: Handles successful authentication
- **handle_error()**: Handles authentication failures

## Example

```python
# Successful desktop login
login._handle_desktop_login()
# Status: "Opening browser for authentication..." (blue)
# Button: disabled
# Browser opens: accounts.google.com OAuth page
# User signs in with Google account
# Browser redirects: http://localhost:8080/callback?code=...
# Local server captures code
# Token exchanged and stored
# Status: "Login successful!" (green)
# on_success() called -> navigate to dashboard

# Failed desktop login (user cancels)
login._handle_desktop_login()
# Status: "Opening browser for authentication..."
# Browser opens
# User cancels OAuth consent
# login_desktop() returns without storing credentials
# is_authenticated() returns False
# Status: "Login completed but authentication failed" (red)
# Button: enabled for retry
```

## See Also

- `handle_login()`: Routes to this for desktop platforms
- `GoogleAuth`: Provides login_desktop()
- `handle_success()`: Called on successful authentication
- `handle_error()`: Called on exceptions

## Notes

- Blocks during authentication (synchronous flow)
- Local server starts on random available port
- Server automatically stops after callback received
- Browser opens automatically via auth service
- User must complete OAuth in browser
- Timeout typically 5 minutes for user to authenticate
- Network errors handled gracefully
- Button re-enabled on failure for retry
- Success callback handles navigation
