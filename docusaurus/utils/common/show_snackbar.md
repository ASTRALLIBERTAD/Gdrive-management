---
id: "show_snackbar"
sidebar_position: 10
title: "show_snackbar"
---

# ⚙️ show_snackbar

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`common.py`](./common.py) | **Line:** 735
:::

Display a transient notification snackbar on a Flet page.

Creates and displays a snackbar at the bottom of the page with the
specified message and background color. Provides temporary user
feedback that auto-dismisses after a few seconds.

## Purpose

- Display temporary notifications to users
        - Provide visual feedback for actions
        - Support color-coded message types (info/success/error/warning)
        - Auto-dismiss after brief period

## Parameters

- **`page`** (ft.Page): Flet page instance where snackbar will be displayed. Must be active and rendered.
- **`message`** (str): Text message to display in snackbar. Should be concise and informative. Examples: "File saved", "Upload complete", "Error: Connection failed".
- **`color`** (ft.Colors, optional): Background color for snackbar. Used to indicate message type (blue=info, green=success, red=error, orange=warning). Defaults to ft.Colors.BLUE.

## Returns

**Type**: `None`


## Algorithm

- 1. **Create Snackbar**:
- a. Instantiate ft.SnackBar
- b. Set content to ft.Text(message)
- c. Set bgcolor to specified color

- 2. **Attach to Page**:
- a. Assign snackbar to page.snack_bar
- b. Replaces any existing snackbar

- 3. **Show Snackbar**:
- a. Set page.snack_bar.open = True
- b. Makes snackbar visible

- 4. **Update Page**:
- a. Call page.update()
- b. Renders snackbar at bottom of screen

## Interactions

- **ft.SnackBar**: Creates notification component
- **ft.Text**: Message content
- **ft.Page**: Displays and updates snackbar

## Example

```python
# Success message
show_snackbar(page, "Assignment saved!", ft.Colors.GREEN)

# Error message
show_snackbar(page, "Upload failed", ft.Colors.RED)

# Info message (default color)
show_snackbar(page, "Loading...")

# Warning message
show_snackbar(page, "Disk space low", ft.Colors.ORANGE)
```

## See Also

- `create_dialog()`: Alternative for modal dialogs
- `ft.SnackBar`: Flet snackbar component

## Notes

- Snackbar appears at bottom of screen
- Auto-dismisses after a few seconds (Flet default)
- Only one snackbar visible at a time (new replaces old)
- Non-blocking (doesn't pause execution)
- Color coding helps indicate message type
- Message should be brief for readability
