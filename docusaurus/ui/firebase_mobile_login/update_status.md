---
id: "update_status"
sidebar_position: 6
title: "update_status"
---

# ⚙️ update_status

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`firebase_mobile_login.py`](./firebase_mobile_login.py) | **Line:** 550
:::

Update the status message displayed to the user.

Modifies the status text content and color to reflect the current
authentication state. Used throughout the login flow to provide
real-time feedback to the user.

## Parameters

- **`message`** (str): Status message to display to user. Examples: "Opening browser...", "Waiting for sign-in...", "Authentication complete!", "Error: ...". Should be concise and informative.
- **`color`** (ft.Colors, optional): Text color for the status message. Used to indicate status type (blue=info, orange=warning, green=success, red=error). Defaults to ft.Colors.BLUE_600.

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

  - 3. **Refresh UI**:
    - a. Call self.page.update()
    - b. Flet re-renders affected components
    - c. User sees updated message and color

## Interactions

- **ft.Text**: Modifies value and color properties
- **ft.Page**: Calls update() to render changes

## Example

```python
# Show initial state
login.update_status(
    "Sign in with your Google account",
    ft.Colors.GREY_700
    )

# Show progress
login.update_status(
    "Opening browser...",
    ft.Colors.ORANGE
    )

# Show waiting state
login.update_status(
    "Waiting for sign-in...",
    ft.Colors.BLUE_600
    )

# Show success
login.update_status(
    "Authentication complete!",
    ft.Colors.GREEN_600
    )

# Show error
login.update_status(
    "Error: Invalid credentials",
    ft.Colors.RED_600
    )
```

## See Also

- `handle_login()`: Uses this to show progress
- `_handle_tokens()`: Uses this to show success/failure
- `_handle_timeout()`: Uses this to show timeout

## Notes

- Called multiple times throughout authentication flow
- Color coding follows standard conventions (green=success, red=error)
- Message should be user-friendly and concise
- Page update is synchronous (blocks until render complete)
- Status text centered in UI for visibility
