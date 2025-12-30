---
id: "update_status"
sidebar_position: 6
title: "update_status"
---

# ⚙️ update_status

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`login.py`](./login.py) | **Line:** 458
:::

Update the status message and optionally control button state.

Modifies the status text content and color to reflect the current
authentication state. Optionally disables or enables the login button
to prevent user actions during processing. Used throughout the login
flow to provide real-time feedback.

## Parameters

- **`message`** (str): Status message to display to user. Examples: "Please log in to continue", "Opening browser...", "Login successful!", "Login failed: ...". Should be concise and user-friendly.
- **`color`** (ft.Colors, optional): Text color for the status message. Used to indicate status type (blue=info, orange=warning, green=success, red=error). Defaults to ft.Colors.BLUE_600.
- **`disable_button`** (bool or None, optional): If provided, sets the login button's disabled state. True disables button (during auth), False enables button (after completion/error), None leaves current state unchanged. Defaults to None.

## Returns

**Type**: `None`


## Algorithm

- 1. **Update Status Text**:
    - a. Access self.status_text.value property
    - b. Assign message parameter to value
    - c. Text content updated in component state

  - 2. **Update Text Color**:
    - a. Access self.status_text.color property
    - b. Assign color parameter to color
    - c. Color updated in component state

  - 3. **Update Button State** (if disable_button provided):
    - a. Check if disable_button parameter is not None
    - b. If not None:
    - i. Access self.login_button.disabled property
    - ii. Assign disable_button value to disabled
    - iii. Button state updated (True=disabled, False=enabled)
    - c. If None: button state unchanged

  - 4. **Refresh UI**:
    - a. Call self.page.update()
    - b. Flet re-renders affected components
    - c. User sees updated message, color, and button state

## Interactions

- **ft.Text**: Modifies value and color properties
- **ft.ElevatedButton**: Modifies disabled property
- **ft.Page**: Calls update() to render changes

## Example

```python
# Show initial state
login.update_status(
    "Please log in to continue",
    ft.Colors.GREY_700,
    disable_button=False
    )

# Show progress (disable button)
login.update_status(
    "Opening browser for authentication...",
    ft.Colors.BLUE_600,
    disable_button=True
    )

# Show success (leave button disabled)
login.update_status(
    "Login successful!",
    ft.Colors.GREEN_600,
    disable_button=None
    )

# Show error (re-enable button)
login.update_status(
    "Login failed: Invalid credentials",
    ft.Colors.RED_600,
    disable_button=False
    )
```

## See Also

- `handle_success()`: Uses this to show success
- `handle_error()`: Uses this to show errors
- `handle_login()`: Uses this to show progress

## Notes

- Called multiple times throughout authentication flow
- Color coding follows standard conventions (green=success, red=error)
- Message should be user-friendly and concise
- disable_button parameter provides fine control over button state
- Page update is synchronous (blocks until render complete)
- Status text centered in UI for visibility
- Button disable prevents double-click during authentication
