---
id: "__init__"
sidebar_position: 11
title: "__init__"
---

# 🔧 __init__

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`login.py`](./login.py) | **Line:** 900
:::

Initialize LoginView with OAuth provider and configuration.

Constructs the login view by storing the OAuth provider reference
and delegating UI construction to the parent LoginBase class.

## Parameters

- **`page`** (ft.Page): Flet page instance for UI updates and platform detection. Must be initialized and active.
- **`provider`** (GoogleOAuthProvider): Flet OAuth provider containing OAuth 2.0 configuration (client_id, client_secret, redirect_url, scopes). Must be properly configured with Google Cloud Console credentials.
- **`auth_service`** (GoogleAuth): Authentication service for token management and credential storage. Must provide login_desktop() method and is_authenticated() check.
- **`on_success`** (Callable, optional): Callback function invoked after successful authentication. Signature: () -> None. Defaults to None.

## Algorithm

- 1. **Store OAuth Provider**:
    - a. Assign provider parameter to self.provider
    - b. Makes provider available to authentication methods

  - 2. **Initialize Parent Class**:
    - a. Call super().__init__() with page, auth_service, on_success
    - b. Parent constructs UI components
    - c. Parent stores page, auth, and callback references
    - d. Component ready for rendering

## Interactions

- **LoginBase.__init__()**: Parent class initialization
- **GoogleOAuthProvider**: OAuth configuration storage

## Example

```python
# Create OAuth provider
provider = GoogleOAuthProvider(
    client_id='client_id',
    client_secret='secret',
    redirect_url='http://localhost:8080/callback'
    )

# Create login view
login = LoginView(
    page=page,
    provider=provider,
    auth_service=auth,
    on_success=lambda: page.go('/dashboard')
    )

# Access provider in methods
print(login.provider.client_id)
# client_id
```

## See Also

- `LoginBase.__init__()`: Parent class initialization
- `GoogleOAuthProvider`: Provider class

## Notes

- Provider stored before parent initialization
- Provider accessible in all instance methods
- Parent __init__ builds UI components
- All LoginBase attributes inherited
