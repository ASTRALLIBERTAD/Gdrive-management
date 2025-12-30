---
id: "_build_oauth_url"
sidebar_position: 8
title: "_build_oauth_url"
---

# ⚙️ _build_oauth_url

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`firebase_mobile_login.py`](./firebase_mobile_login.py) | **Line:** 784
:::

Construct the Google OAuth 2.0 authorization URL with parameters.

Builds a complete OAuth URL including client ID, scopes, redirect URI,
and state parameter for initiating the authentication flow. Uses
implicit grant flow which returns tokens directly in URL fragment.

## Returns

**Type**: `str`

                Format: 'https://accounts.google.com/o/oauth2/v2/auth?param=value&...'
                Includes all required OAuth parameters URL-encoded.

## Algorithm

- 1. **Set Base URL**:
    - a. Define auth_url as Google OAuth 2.0 endpoint
    - b. Value: "https://accounts.google.com/o/oauth2/v2/auth"
    - c. This is Google's standard authorization endpoint

  - 2. **Define OAuth Parameters**:
    - a. Create params dictionary with key-value pairs:
    - - client_id: self.oauth_client_id
    - (identifies the application to Google)
    - - redirect_uri: callback server URL
    - (where Google sends user after auth)
    - Value: 'https://lms-callback-git-main-astrallibertads-projects.vercel.app/callback.html'
    - - response_type: 'token'
    - (implicit grant - returns access_token in URL fragment)
    - - scope: space-separated OAuth scopes
    - Value: 'openid email profile https://www.googleapis.com/auth/drive'
    - (requests OpenID, user info, and Drive access)
    - - state: self.session_id
    - (CSRF protection and callback server token lookup key)

  - 3. **Encode Parameters**:
    - a. Call urllib.parse.urlencode(params)
    - b. Converts dictionary to URL query string
    - c. Example: 'client_id=123&redirect_uri=https%3A%2F%2F...'
    - d. Special characters percent-encoded for URL safety

  - 4. **Construct Complete URL**:
    - a. Format string: f"&#123;auth_url&#125;?&#123;encoded_params&#125;"
    - b. Combines base URL with encoded parameters
    - c. Result: full OAuth authorization URL

  - 5. **Return URL**:
    - a. Return complete URL string for browser launch

## Interactions

- **urllib.parse.urlencode()**: Encodes parameters for URL
- **self.oauth_client_id**: Application OAuth client ID
- **self.session_id**: Unique session identifier for state param

## Example

```python
login.session_id = 'abc123xyz'
login.oauth_client_id = '456-def.apps.googleusercontent.com'
url = login._build_oauth_url()
print(url)
# https://accounts.google.com/o/oauth2/v2/auth?client_id=456-def.apps.googleusercontent.com&redirect_uri=https%3A%2F%2Flms-callback...&response_type=token&scope=openid+email+profile+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdrive&state=abc123xyz

# URL components:
# - Base: accounts.google.com/o/oauth2/v2/auth
# - client_id: identifies app
# - redirect_uri: callback URL (encoded)
# - response_type: token (implicit grant)
# - scope: permissions requested (spaces -> +)
# - state: session ID for CSRF protection
```

## See Also

- `handle_login()`: Calls this to get OAuth URL
- `urllib.parse`: URL encoding utilities

## Notes

- Uses implicit grant flow (response_type=token)
- Tokens returned in URL fragment (#access_token=...), not query
- Callback URL must be authorized in Google Cloud Console
- Scopes request OpenID, profile, email, and Drive access
- State parameter (session_id) prevents CSRF attacks
- Redirect URI points to callback server that stores tokens
- URL encoding handles special characters in parameters
- Scope parameter uses space-separated values (encoded as +)
