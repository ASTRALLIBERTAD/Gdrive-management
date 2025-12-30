---
id: "firebasemobilelogin"
sidebar_position: 2
title: "FirebaseMobileLogin"
---

# 📦 FirebaseMobileLogin

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Completeness](https://img.shields.io/badge/Docs-20%25-red)

:::info Source
**File:** [`firebase_mobile_login.py`](./firebase_mobile_login.py) | **Line:** 31
:::

Mobile-friendly OAuth 2.0 authentication component for Google sign-in.

FirebaseMobileLogin is a specialized Flet UI component that provides a complete
mobile authentication workflow for the Learning Management System. It addresses
the limitation of mobile platforms where native OAuth popup windows are unavailable
by launching an external browser for authentication, then polling a callback server
to retrieve the OAuth tokens once the user completes sign-in.
This component implements a secure OAuth 2.0 implicit grant flow with state
parameter validation, background polling for token retrieval, and comprehensive
error handling. It integrates seamlessly with the application's authentication
service and provides real-time status updates throughout the login process.

## Purpose

- Provide mobile-compatible Google OAuth 2.0 authentication interface
        - Launch external browser for user sign-in on mobile platforms
        - Poll callback server to retrieve OAuth tokens after authentication
        - Handle authentication flow with progress indicators and status updates
        - Integrate with application's authentication service for token management
        - Support platform detection and responsive UI for various mobile devices

## Attributes

- **`page`** (ft.Page): Flet page instance providing UI rendering, updates, and platform detection. Used for launching external URLs and running async UI update tasks.
- **`auth`** (GoogleAuth): Authentication service managing OAuth token storage, credential validation, and Drive API service initialization. Provides login_with_token() method for token processing.
- **`firebase_config`** (dict): Firebase project configuration containing API keys, project ID, auth domain, and other Firebase-specific settings. Used for Firebase integration if needed (currently OAuth-focused).
- **`oauth_client_id`** (str): Google OAuth 2.0 client ID for authentication requests. Must match the client ID configured in Google Cloud Console with authorized redirect URIs.
- **`on_success`** (Callable or None): Optional callback function with no parameters, invoked after successful authentication. Typically navigates to dashboard or main application view. Signature: () -> None.
- **`session_id`** (str or None): Unique session identifier generated using secrets.token_urlsafe(16). Used as OAuth state parameter for CSRF protection and callback server token retrieval. None before login initiated.
- **`polling`** (bool): Flag indicating whether background token polling thread is active. Set to True when polling starts, False when tokens received or timeout occurs. Controls polling loop continuation.
- **`status_text`** (ft.Text): UI text element displaying current authentication status messages to user. Color changes to indicate progress, success, or errors. Updated throughout login flow.
- **`login_button`** (ft.ElevatedButton): Primary action button for initiating Google sign-in. Disabled during authentication process, re-enabled on timeout or error.
- **`progress`** (ft.ProgressRing): Circular progress indicator shown during authentication. Visible while waiting for user to complete sign-in and during token processing. Hidden when idle or complete.

## Interactions

- **GoogleAuth**: Calls login_with_token() to process OAuth credentials
- **ft.Page**: Uses launch_url() to open browser, run_task() for async updates
- **Callback Server**: Polls HTTPS endpoint for token retrieval via urllib
- **Google OAuth**: External browser navigates to accounts.google.com for auth
- **secrets module**: Generates cryptographically secure session IDs
- **threading module**: Runs background polling in daemon thread
- **urllib**: Makes HTTP requests to callback server for token checking
- **json module**: Parses JSON responses from callback server
- Algorithm (High-Level Workflow):
- *Phase 1: Initialization**
- 1. Call parent ft.Column constructor with layout settings
- 2. Store references to page, auth service, firebase config, client ID
- 3. Initialize session_id to None and polling flag to False
- 4. Initialize UI component references (status_text, login_button, progress)
- 5. Call _build_ui() to construct and arrange interface elements
- *Phase 2: UI Construction** (_build_ui)
- 1. Detect platform name for display (Android, iOS, etc.)
- 2. Add header components (icon, title, subtitle)
- 3. Create status text element for progress messages
- 4. Create login button with Google branding and styling
- 5. Create progress ring (initially hidden)
- 6. Append all components to self.controls list
- *Phase 3: Login Initiation** (handle_login)
- 1. Generate unique session_id using secrets.token_urlsafe(16)
- 2. Update status to "Opening browser..." (orange color)
- 3. Disable login button and show progress indicator
- 4. Construct OAuth URL with client ID, scopes, and session_id as state
- 5. Launch external browser with OAuth URL via page.launch_url()
- 6. Update status to "Waiting for sign-in..." (blue color)
- 7. Start background polling thread via _start_polling()
- *Phase 4: Background Token Polling** (_start_polling)
- 1. Set polling flag to True
- 2. Create daemon thread for polling loop
- 3. Start thread to run in background (non-blocking)
- 4. Polling loop (in thread):
- a. Maximum 60 attempts, 5-second intervals (5 minutes total)
- b. For each attempt:
- Update waiting status with animated dots
- Send GET request to callback server with session_id
- Parse JSON response for token data
- If access_token found: call _handle_tokens() and exit loop
- If HTTP error or no token: wait 5 seconds, retry
- c. If max attempts reached without token: call _handle_timeout()
- *Phase 5: Token Processing** (_handle_tokens)
- 1. Stop polling by setting flag to False
- 2. Update status to "Authenticating..." (green color)
- 3. Construct token_data dictionary with access_token and metadata
- 4. Call auth.login_with_token(token_data) to process credentials
- 5. If authentication successful:
- a. Update status to "Authentication complete!" (green)
- b. Hide progress indicator
- c. Invoke on_success() callback if provided
- 6. If authentication failed:
- a. Update status to "Authentication failed" (red)
- b. Re-enable login button for retry
- c. Hide progress indicator
- *Phase 6: Timeout Handling** (_handle_timeout)
- 1. Stop polling by setting flag to False
- 2. Update status to "Timeout - Sign-in took too long" (orange)
- 3. Re-enable login button to allow retry
- 4. Hide progress indicator
- 5. User can click login button to start new session

## Example

```python
# Setup configuration
firebase_config = {
    'apiKey': 'AIza...',
    'projectId': 'my-project'
    }
oauth_client_id = '123456-abc.apps.googleusercontent.com'

# Define success handler
def on_login_success():
    page.go('/dashboard')
    print('Login successful!')

# Create login component
login = FirebaseMobileLogin(
    page=page,
    auth_service=auth,
    firebase_config=firebase_config,
    oauth_client_id=oauth_client_id,
    on_success=on_login_success
    )

# Add to page
page.add(login)
page.update()

# User clicks "Sign in with Google" button
# 1. Browser opens to Google sign-in page
# 2. User authenticates with Google account
# 3. Callback server receives OAuth token
# 4. Polling loop retrieves token
# 5. auth.login_with_token() processes credentials
# 6. on_login_success() called -> navigates to dashboard
```

## See Also

- `GoogleAuth`: Authentication service
- `LoginView`: Desktop OAuth login implementation
- `secrets`: Cryptographic random number generation
- `threading`: Thread-based parallelism for background polling
- `Google OAuth 2.0 <[https://developers.google.com/identity/protocols/oauth2>`_](https://developers.google.com/identity/protocols/oauth2>`_)

## Notes

- Uses OAuth 2.0 implicit grant flow (response_type=token)
- Tokens returned in URL fragment, not query string
- Callback server temporarily stores tokens indexed by session_id
- Polling runs for maximum 5 minutes (60 x 5 seconds)
- State parameter (session_id) provides CSRF protection
- External browser required on mobile (no popup support)
- Progress indicator shows active authentication process
- Login button disabled during authentication to prevent double-click
- All UI updates run on main thread via page.run_task()
- Polling thread is daemon thread (exits when app closes)

## Security Considerations

:::note
- session_id provides CSRF protection via OAuth state parameter
        - Tokens retrieved over HTTPS from callback server
        - Access tokens have limited lifetime (expires_in)
        - Client secret managed by auth service, not exposed in UI
        - Callback server should validate redirect URIs
:::

## References

- OAuth 2.0 Implicit Grant: [https://oauth.net/2/grant-types/implicit/](https://oauth.net/2/grant-types/implicit/)
- Flet Documentation: [https://flet.dev/docs/](https://flet.dev/docs/)
- Google OAuth Scopes: [https://developers.google.com/identity/protocols/oauth2/scopes](https://developers.google.com/identity/protocols/oauth2/scopes)
