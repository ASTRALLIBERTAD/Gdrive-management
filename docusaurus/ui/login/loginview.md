---
id: "loginview"
sidebar_position: 10
title: "LoginView"
---

# 📦 LoginView

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Completeness](https://img.shields.io/badge/Docs-20%25-red)

:::info Source
**File:** [`login.py`](./login.py) | **Line:** 772
:::

Concrete login implementation with OAuth provider and platform detection.

LoginView extends LoginBase to provide a complete login solution that
automatically detects the platform (desktop vs mobile) and executes the
appropriate OAuth 2.0 authentication flow. Desktop platforms use a local
HTTP server for OAuth callback handling, while mobile platforms launch
an external browser with redirect-based authentication.

## Purpose

- Provide platform-aware OAuth 2.0 authentication
        - Support desktop login with local callback server
        - Support mobile login with browser redirect
        - Integrate with GoogleOAuthProvider for OAuth configuration
        - Handle platform detection and flow selection automatically
        - Provide seamless authentication experience across all platforms

## Attributes

- **`provider`** (GoogleOAuthProvider): Flet OAuth provider instance containing OAuth configuration (client_id, client_secret, redirect_url, scopes). Used for building OAuth URLs and handling callbacks.
- **`page`** (ft.Page): Inherited from LoginBase. Flet page instance.
- **`auth`** (GoogleAuth): Inherited from LoginBase. Authentication service.
- **`on_success`** (Callable): Inherited from LoginBase. Success callback.
- **`status_text`** (ft.Text): Inherited from LoginBase. Status display.
- **`login_button`** (ft.ElevatedButton): Inherited from LoginBase. Login button.

## Interactions

- **LoginBase**: Parent class providing UI framework and common methods
- **GoogleOAuthProvider**: Provides OAuth configuration and credentials
- **GoogleAuth**: Handles token storage and authentication validation
- **ft.Page**: Platform detection and browser launching
- **urllib.parse**: URL encoding for OAuth parameters
- Algorithm (High-Level Workflow):
- *Phase 1: Initialization**
- 1. Store OAuth provider reference
- 2. Call parent LoginBase.__init__() to build UI
- 3. Component ready for rendering
- *Phase 2: Login Initiation** (handle_login)
- 1. Detect platform type (desktop vs mobile)
- 2. Check if platform in [WINDOWS, LINUX, MACOS]
- 3. If desktop: call _handle_desktop_login()
- 4. If mobile: call _handle_mobile_login()
- *Phase 3: Desktop Authentication** (_handle_desktop_login)
- 1. Update status to "Opening browser for authentication..."
- 2. Disable login button
- 3. Call auth.login_desktop() - starts local server, opens browser
- 4. Wait for user to complete OAuth in browser
- 5. Check auth.is_authenticated()
- 6. If authenticated: call handle_success()
- 7. If not authenticated: show error message
- 8. On exception: call handle_error()
- *Phase 4: Mobile Authentication** (_handle_mobile_login)
- 1. Update status to "Opening browser..."
- 2. Disable login button
- 3. Build OAuth URL with authorization code flow parameters
- 4. Include client_id, redirect_uri, scopes, access_type, prompt
- 5. Launch external browser with OAuth URL
- 6. Update status with instruction to return to app
- 7. Show snackbar notification about browser opening
- 8. User completes auth in browser (handled externally)
- 9. On exception: call handle_error()

## Example

```python
# Setup OAuth provider
from flet.auth.providers import GoogleOAuthProvider
provider = GoogleOAuthProvider(
    client_id='123456-abc.apps.googleusercontent.com',
    client_secret='secret_key',
    redirect_url='http://localhost:8080/callback'
    )

# Define success callback
def on_login_success():
    page.go('/dashboard')
    print('Login successful!')

# Create login view
login = LoginView(
    page=page,
    provider=provider,
    auth_service=auth,
    on_success=on_login_success
    )

# Add to page
page.add(login)
page.update()

# Desktop user clicks login:
# -> Browser opens to accounts.google.com
# -> User signs in with Google account
# -> Browser redirects to localhost:8080/callback
# -> Local server captures OAuth code
# -> Token exchanged and stored
# -> on_login_success() called -> dashboard

# Mobile user clicks login:
# -> Browser opens to accounts.google.com
# -> User signs in with Google account
# -> Browser redirects to configured callback URL
# -> External callback handler processes token
# -> User returns to app manually
```

## See Also

- `LoginBase`: Parent class with UI framework
- `FirebaseMobileLogin`: Alternative mobile implementation
- `GoogleAuth`: Authentication service
- `GoogleOAuthProvider`: OAuth provider configuration

## Notes

- Platform detection based on ft.PagePlatform enum
- Desktop platforms: Windows, Linux, macOS
- Mobile platforms: Android, iOS
- Desktop uses authorization code flow with local server
- Mobile uses authorization code flow with external callback
- Both flows require OAuth 2.0 client credentials
- Provider must be configured with correct redirect URLs
- Desktop redirect: typically `http://localhost:&#123;PORT&#125;/callback`
- Mobile redirect: must match OAuth client configuration
- Error handling consistent across both flows
- Success callback shared between desktop and mobile flows
