---
id: "main"
sidebar_position: 6
title: "main"
---

# ⚙️ main

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`main.py`](./main.py) | **Line:** 425
:::

Main application entry point and Flet page handler.

Initializes and manages the entire LMS application lifecycle including
OAuth configuration, authentication state management, and view routing.
Handles both desktop and mobile platforms with appropriate login flows
and provides comprehensive error handling for initialization failures.

## Purpose

- Initialize Flet application and page configuration
        - Setup OAuth authentication services
        - Manage authentication state and routing
        - Handle platform-specific login flows (desktop vs mobile)
        - Provide dashboard access for authenticated users
        - Handle logout and re-authentication

## Parameters

- **`page`** (ft.Page): Flet page instance provided by the Flet runtime. Represents the application window/screen and provides access to UI controls, platform detection, and event handling. Modified throughout function to display different views.

## Returns

**Type**: `None`

            application lifecycle until user exits.

## Exceptions

Exception: Critical errors during initialization displayed on page
            with error message and stack trace. Application continues running
            in error state to allow debugging.

## Algorithm

- **Phase 1: Page Configuration**
  - 1. Set page.title = "LMS Alternative"
  - 2. Set page.theme_mode = LIGHT
  - 3. Set page.bgcolor = WHITE
  - 4. Set page.padding = 0 (full-screen layout)

- **Phase 2: Environment Setup**
  - 1. Call setup_paths() to configure imports
  - 2. Store returned app_path and cwd
  - 3. Call repair_filesystem(cwd) to fix Android issues

- **Phase 3: Module Imports**
  - 1. Import GoogleAuth from services.auth_service
  - 2. Import Dashboard from ui.dashboard
  - 3. Import LoginView from ui.login
  - 4. Try to import FirebaseMobileLogin:
    - a. If ImportError, set to None (not available)

- **Phase 4: Credentials Loading**
  - 1. Call load_credentials(app_path, cwd)
  - 2. If creds is None:
    - a. Display error: "ERROR: web.json not found!"
    - b. Return early (cannot proceed without credentials)

- **Phase 5: OAuth Provider Setup**
  - 1. Get redirect URL via get_redirect_url()
  - 2. Create GoogleAuth service with credentials file
  - 3. Create GoogleOAuthProvider with:
    - a. client_id from credentials
    - b. client_secret from credentials
    - c. redirect_url from get_redirect_url()
  - 4. Set provider.scopes = ["openid", "email", "profile"]

- **Phase 6: Define Handler Functions**

  - **handle_on_login(e)** - OAuth callback handler:
    - 1. Check if e.error exists (auth failed)
    - 2. If error, show snackbar and return
    - 3. Verify page.auth.token exists
    - 4. If no token, show error and return
    - 5. Extract token_data from page.auth.token
    - 6. If dict, add client_id and client_secret
    - 7. Call auth_service.login_with_token(token_data)
    - 8. If successful, show_dashboard()
    - 9. If failed, show error snackbar

  - **show_snackbar(message)** - Display notification:
    - 1. Create SnackBar with message
    - 2. Set action to "Dismiss"
    - 3. Set open = True
    - 4. Call page.update()

  - **show_dashboard()** - Display main application:
    - 1. Clear page.controls
    - 2. Create Dashboard instance with:
    - a. page reference
    - b. auth_service
    - c. handle_logout callback
    - 3. Get dashboard view via get_view()
    - 4. Add to page
    - 5. Call page.update()

  - **handle_logout()** - Process user logout:
    - 1. Call auth_service.logout() to clear credentials
    - 2. If page.auth has logout method, call it
    - 3. Call show_login() to return to login screen

  - **show_login()** - Display login view:
    - 1. Clear page.controls
    - 2. Detect platform: is_mobile = platform in [ANDROID, IOS]
    - 3. If mobile and FirebaseMobileLogin available:
    - a. Load firebase_config.json if exists
    - b. Create FirebaseMobileLogin with config
    - c. Add to page
    - 4. Else (desktop):
    - a. Create LoginView with provider
    - b. Add to page
    - 5. Call page.update()

- **Phase 7: Register OAuth Callback**
  - 1. Set page.on_login = handle_on_login
  - 2. Flet calls this when OAuth completes

- **Phase 8: Initial Route**
  - 1. Check if auth_service.is_authenticated()
  - 2. If True: call show_dashboard()
  - 3. If False: call show_login()

- **Phase 9: Error Handling**
  - 1. Outer try-except catches all initialization errors
  - 2. On exception:
    - a. Import traceback
    - b. Format full stack trace
    - c. Display error message on page (red text)
    - d. Print full traceback to console
    - e. Application remains in error state

## Interactions

- **setup_paths()**: Configures import paths
- **repair_filesystem()**: Fixes Android file issues
- **load_credentials()**: Loads OAuth configuration
- **get_redirect_url()**: Gets OAuth redirect URL
- **GoogleAuth**: Manages authentication state
- **GoogleOAuthProvider**: Configures OAuth flow
- **Dashboard**: Main application view (authenticated)
- **LoginView**: Desktop login view
- **FirebaseMobileLogin**: Mobile login view (optional)
- **ft.Page**: Application window/screen management

## Example

```python
# Flet automatically calls main with page instance
import flet as ft
ft.app(target=main)

# Application flow:
# 1. main(page) called by Flet
# 2. Page configured and OAuth setup
# 3. Check authentication state
# 4a. If authenticated -> Dashboard shown
# 4b. If not authenticated -> Login shown
# 5. User logs in -> OAuth callback -> Dashboard
# 6. User clicks logout -> Login shown again
```

## See Also

- `setup_paths()`: Configures module imports
- `load_credentials()`: Loads OAuth config
- `repair_filesystem()`: Fixes Android issues
- `GoogleAuth`: Authentication service
- `Dashboard`: Main application view
- `LoginView`: Desktop login
- `FirebaseMobileLogin`: Mobile login
- `GoogleOAuthProvider`: OAuth provider

## Notes

- Entry point for entire application
- Handles both desktop (Windows, macOS, Linux) and mobile (Android, iOS)
- OAuth scopes: openid, email, profile (basic user info)
- FirebaseMobileLogin optional (gracefully degrades if not available)
- Nested functions access outer scope variables (closures)
- Critical errors displayed on page (doesn't crash silently)
- Authentication state checked on startup
- Page cleared between view transitions
- Dashboard requires authentication (checks on entry)
- Logout returns to login screen (clears session)
