---
id: "handle_success"
sidebar_position: 7
title: "handle_success"
---

# ⚙️ handle_success

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`login.py`](./login.py) | **Line:** 560
:::

Handle successful authentication completion.

Updates the UI to display success message and invokes the success
callback to navigate to the main application view. Called by subclass
implementations after successful OAuth token retrieval and validation.

## Returns

**Type**: `None`


## Algorithm

- 1. **Update Status Display**:
    - a. Call update_status() with success message
    - b. Message: "Login successful!"
    - c. Color: ft.Colors.GREEN_600 (success color)
    - d. Button state: not changed (remains in current state)

  - 2. **Invoke Success Callback**:
    - a. Check if self.on_success is not None
    - b. If callback exists:
    - i. Call self.on_success()
    - ii. Callback typically navigates to dashboard
    - iii. May perform additional setup (load user data, etc.)
    - c. If callback is None:
    - i. No action taken
    - ii. UI shows success message only

## Interactions

- **update_status()**: Shows success message to user
- **on_success callback**: Invoked for post-login navigation

## Example

```python
# Define success callback
def on_login_success():
    page.go('/dashboard')
    load_user_data()
    print('Login complete')

login = LoginView(page, provider, auth, on_login_success)

# After successful authentication
login.handle_success()
# Status: "Login successful!" (green)
# on_login_success() called
# User navigated to dashboard
```

## See Also

- `update_status()`: Updates status message
- `handle_error()`: Handles authentication failures
- `handle_login()`: Initiates authentication flow

## Notes

- Called by subclass after successful OAuth token validation
- Success callback is optional (None check performed)
- Callback should handle navigation and post-login setup
- UI update provides visual confirmation before navigation
- Button state not explicitly changed (typically already disabled)
- Callback may trigger page navigation (removes login view)
