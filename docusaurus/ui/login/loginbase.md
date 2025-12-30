---
id: "loginbase"
sidebar_position: 2
title: "LoginBase"
---

# 📦 LoginBase

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Completeness](https://img.shields.io/badge/Docs-20%25-red)

:::info Source
**File:** [`login.py`](./login.py) | **Line:** 22
:::

Abstract base class for login UI components with common authentication elements.

LoginBase provides a reusable foundation for building login interfaces across
different platforms and authentication flows. It encapsulates common UI elements
(logo, title, status messages, login button) and defines a standard interface
for handling authentication events. Subclasses implement platform-specific
OAuth flows while inheriting the consistent UI structure and error handling.
This class follows the Template Method pattern where the base class provides
the UI framework and delegates authentication logic to subclasses through the
abstract handle_login method. It manages UI state transitions during the
authentication process and provides callbacks for success and error scenarios.

## Purpose

- Provide reusable base class for login UI components
        - Define standard login interface structure and layout
        - Manage authentication status messages and visual feedback
        - Handle success and error scenarios with consistent user experience
        - Abstract platform-specific authentication logic to subclasses
        - Support callback-based navigation after successful login

## Attributes

- **`page`** (ft.Page): Flet page instance for UI rendering, platform detection, and page updates. Provides access to page.platform for device type detection and page.update() for UI refresh.
- **`auth`** (GoogleAuth): Authentication service managing OAuth credentials, token storage, and Drive API service initialization. Provides is_authenticated() check and platform-specific login methods.
- **`on_success`** (Callable or None): Optional callback function with no parameters, invoked after successful authentication. Typically handles navigation to main application view. Signature: () -> None.
- **`status_text`** (ft.Text): UI text element displaying current authentication status and messages to user. Color changes dynamically to indicate state (blue=info, green=success, red=error, grey=neutral).
- **`login_button`** (ft.ElevatedButton): Primary action button for initiating authentication flow. Disabled during authentication process, re-enabled on completion or error. Styled with Google brand colors.

## Interactions

- **ft.Column**: Parent class providing vertical layout container
- **GoogleAuth**: Authentication service for credential management
- **ft.Page**: Page instance for UI updates and platform detection
- **ft.Text**: Status message display with dynamic color
- **ft.ElevatedButton**: Login action button with event handling
- **ft.Icon, ft.Container**: UI components for layout and branding
- Algorithm (High-Level Workflow):
- *Phase 1: Initialization**
- 1. Call parent ft.Column constructor with centered layout settings
- 2. Store references to page, auth service, and success callback
- 3. Call _build_ui() to construct UI component tree
- *Phase 2: UI Construction** (_build_ui)
- 1. Detect platform name for display
- 2. Add header components (icon, title, subtitle, platform info)
- 3. Create status text element for messages
- 4. Create login button with click handler
- 5. Add security notice text
- 6. Append all components to self.controls
- *Phase 3: User Interaction** (handle_login - abstract)
- 1. User clicks login button
- 2. Subclass implementation handles platform-specific OAuth
- 3. Authentication process executes
- 4. Success or error handler invoked based on result
- *Phase 4: Success Handling** (handle_success)
- 1. Update status to "Login successful!" (green)
- 2. Check if on_success callback exists
- 3. If callback exists, invoke it (typically navigates to dashboard)
- *Phase 5: Error Handling** (handle_error)
- 1. Extract error message from exception
- 2. Update status with error description (red)
- 3. Re-enable login button for retry
- 4. Log full error details to console for debugging

## Example

```python
# Define success handler
def on_login_success():
    page.go('/dashboard')
    print('User logged in successfully')

# Create concrete subclass (LoginView)
login = LoginView(
    page=page,
    provider=oauth_provider,
    auth_service=auth,
    on_success=on_login_success
    )

# Add to page
page.add(login)
page.update()

# User sees login UI with:
# - LMS logo and title
# - Status: "Please log in to continue"
# - "Login with Google" button
# - Platform indicator
# - Security notice

# User clicks login button -> subclass handles authentication
# On success -> status turns green -> on_login_success() called
```

## See Also

- `LoginView`: Concrete implementation with OAuth provider
- `FirebaseMobileLogin`: Mobile login alternative
- `GoogleAuth`: Authentication service
- `ft.Column`: Parent Flet container class

## Notes

- Abstract class - cannot be instantiated directly
- Subclasses must implement handle_login method
- UI components stored as instance attributes for dynamic updates
- Status color conventions: grey=neutral, blue=info, green=success, red=error
- Login button automatically disabled during authentication
- Success callback is optional (None check before invocation)
- Platform detection automatic via Flet framework
- All UI updates synchronized via page.update()

## References

- Template Method Pattern: [https://refactoring.guru/design-patterns/template-method](https://refactoring.guru/design-patterns/template-method)
- Flet UI Framework: [https://flet.dev/docs/](https://flet.dev/docs/)
- Google OAuth 2.0: [https://developers.google.com/identity/protocols/oauth2](https://developers.google.com/identity/protocols/oauth2)
