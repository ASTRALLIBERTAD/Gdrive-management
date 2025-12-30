---
id: "_handle_mobile_login"
sidebar_position: 14
title: "_handle_mobile_login"
---

# ⚙️ _handle_mobile_login

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`login.py`](./login.py) | **Line:** 1152
:::

Execute mobile OAuth flow with external browser redirect.

Performs OAuth 2.0 authentication on mobile platforms by launching
the system browser with OAuth URL. Uses authorization code flow with
external redirect URL that must be handled by a callback server or
deep link handler.

## Returns

**Type**: `None`


## Algorithm

- 1. **Import URL Encoding Module**:
    - a. Import urllib.parse for URL parameter encoding
    - b. Used to safely encode OAuth parameters

  - 2. **Update UI for Processing**:
    - a. Call update_status() with progress message
    - b. Message: "Opening browser..."
    - c. Color: default (blue)
    - d. disable_button: True (prevents double-click)

  - 3. **Try Browser Launch**:
    - a. Enter try block for error handling

  - 4. **Build OAuth URL**:
    - a. Set auth_url to Google OAuth endpoint:
    - "https://accounts.google.com/o/oauth2/v2/auth"
    - b. Create params dictionary with OAuth parameters:
    - i. client_id: self.provider.client_id
    - (application identifier from Google Console)
    - ii. redirect_uri: self.provider.redirect_url
    - (where Google sends user after auth)
    - iii. response_type: 'code'
    - (authorization code flow, not implicit)
    - iv. scope: ' '.join(self.provider.scopes)
    - (space-separated list of requested permissions)
    - v. access_type: 'offline'
    - (request refresh token for long-term access)
    - vi. prompt: 'consent'
    - (force consent screen for consistent UX)
    - c. URL-encode parameters: urllib.parse.urlencode(params)
    - d. Build complete URL: f"&#123;auth_url&#125;?&#123;encoded_params&#125;"
    - e. Store in oauth_url variable

  - 5. **Launch External Browser**:
    - a. Call self.page.launch_url(oauth_url)
    - b. Opens system browser to OAuth URL
    - c. Non-blocking operation (returns immediately)
    - d. User sees Google sign-in page in browser

  - 6. **Update UI with Instructions**:
    - a. Call update_status() with instruction message
    - b. Message: "Complete sign-in in browser, then return to app"
    - c. Color: BLUE_600 (informational)
    - d. disable_button: False (re-enable button)
    - e. User can retry if browser doesn't open

  - 7. **Show Snackbar Notification**:
    - a. Create SnackBar with content text
    - b. Content: "Browser opening... Complete sign-in, then return here."
    - c. Add action button: "OK"
    - d. Assign to self.page.snack_bar
    - e. Set snack_bar.open = True
    - f. Call self.page.update() to display snackbar
    - g. Provides additional visual feedback

  - 8. **Handle Exceptions**:
    - a. Catch any Exception during browser launch
    - b. Examples: URLError, OSError
    - c. Call self.handle_error(ex, "Browser launch")
    - d. Shows error message and re-enables button

## Interactions

- **urllib.parse.urlencode()**: Encodes OAuth parameters
- **update_status()**: Shows progress and instructions
- **ft.Page.launch_url()**: Opens external browser
- **ft.SnackBar**: Shows notification about browser
- **handle_error()**: Handles launch failures

## Example

```python
# Successful mobile login initiation
login._handle_mobile_login()
# Status: "Opening browser..." (blue, button disabled)
# Browser opens: accounts.google.com OAuth page
# Status: "Complete sign-in in browser..." (blue, button enabled)
# Snackbar: "Browser opening..."
# User completes OAuth in browser
# Browser redirects to external callback URL
# External handler processes token
# User manually returns to app

# Browser launch failure
login._handle_mobile_login()
# Status: "Opening browser..."
# Exception raised (no browser available)
# Status: "Browser launch failed: ..." (red, button enabled)
# User can retry
```

## See Also

- `handle_login()`: Routes to this for mobile platforms
- `FirebaseMobileLogin`:
- Alternative with polling
- `handle_error()`: Called on exceptions
- `urllib.parse`: URL encoding utilities

## Notes

- Uses authorization code flow (not implicit grant)
- Requires external callback URL handling
- Browser opens asynchronously (non-blocking)
- User must return to app manually after auth
- Redirect URL must be configured in Google Console
- Token exchange handled externally (not in app)
- No automatic token retrieval (unlike desktop flow)
- access_type='offline' requests refresh token
- prompt='consent' shows consent screen every time
- Snackbar provides additional user guidance
- Button re-enabled to allow retry if needed
