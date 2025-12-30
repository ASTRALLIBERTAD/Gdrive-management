---
id: "__init__"
sidebar_position: 3
title: "__init__"
---

# 🔧 __init__

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`firebase_mobile_login.py`](./firebase_mobile_login.py) | **Line:** 221
:::

Initialize the FirebaseMobileLogin component with configuration and callbacks.

Constructs the mobile OAuth login interface by setting up references to
required services, initializing state variables, and building the UI
component tree. Prepares the component for rendering and user interaction.

## Parameters

- **`page`** (ft.Page): Flet page instance for UI updates, platform detection, and URL launching. Must be initialized and active. Provides access to page.platform (device type) and page.launch_url() (browser).
- **`auth_service`** (GoogleAuth): Authentication service for OAuth token processing and credential management. Must provide login_with_token() method and client_secret attribute.
- **`firebase_config`** (dict): Firebase project configuration dictionary containing keys like 'apiKey', 'projectId', 'authDomain'. Used for potential Firebase integration. Required parameter but currently OAuth-focused implementation.
- **`oauth_client_id`** (str): Google OAuth 2.0 client ID string from Google Cloud Console. Must be authorized with callback redirect URI. Format: '123456-abc.apps.googleusercontent.com'
- **`on_success`** (Callable, optional): Callback function invoked after successful authentication. Should handle navigation to main app view. Signature: () -> None. Defaults to None (no action).

## Algorithm

- 1. **Initialize Parent Column**:
    - a. Call super().__init__() with layout configuration
    - b. Set controls to empty list (populated by _build_ui)
    - c. Set alignment to MainAxisAlignment.CENTER (vertical centering)
    - d. Set horizontal_alignment to CrossAxisAlignment.CENTER
    - e. Set expand=True to fill available space
    - f. Set spacing=20 between child components

  - 2. **Store Service References**:
    - a. Assign page parameter to self.page
    - b. Assign auth_service to self.auth
    - c. Assign firebase_config to self.firebase_config
    - d. Assign oauth_client_id to self.oauth_client_id
    - e. Assign on_success callback to self.on_success

  - 3. **Initialize Session State**:
    - a. Set self.session_id to None (no active session yet)
    - b. Set self.polling to False (no background polling active)

  - 4. **Initialize UI Component References**:
    - a. Set self.status_text to None (created in _build_ui)
    - b. Set self.login_button to None (created in _build_ui)
    - c. Set self.progress to None (created in _build_ui)

  - 5. **Build User Interface**:
    - a. Call self._build_ui()
    - b. Constructs all UI components
    - c. Populates self.controls with component tree
    - d. Stores references to key components for later updates
    - e. Component now ready for rendering

## Interactions

- **ft.Column**: Parent class constructor for layout configuration
- **_build_ui()**: Called to construct UI component tree

## Example

```python
# Create with minimal configuration
login = FirebaseMobileLogin(
    page=page,
    auth_service=auth,
    firebase_config={'apiKey': 'key123'},
    oauth_client_id='client_id',
    on_success=None
    )
print(f"Session ID: {login.session_id}")
# Session ID: None
print(f"Polling active: {login.polling}")
# Polling active: False

# Create with success callback
def navigate_to_dashboard():
    page.go('/dashboard')

login_with_callback = FirebaseMobileLogin(
    page=page,
    auth_service=auth,
    firebase_config=config,
    oauth_client_id='client_id',
    on_success=navigate_to_dashboard
    )
```

## See Also

- `_build_ui()`: Constructs the UI component tree
- `GoogleAuth`: Auth service requirements
- `ft.Column`: Parent Flet column container

## Notes

- Component is a Flet Column, can be added directly to page
- UI components created in _build_ui, not in __init__
- Session state initialized to inactive (no polling, no session)
- on_success callback is optional (None check before invocation)
- All parameters except on_success are required
- Component ready for rendering immediately after initialization
