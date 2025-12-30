---
id: "create_icon_button"
sidebar_position: 9
title: "create_icon_button"
---

# ⚙️ create_icon_button

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`common.py`](./common.py) | **Line:** 650
:::

Create a standard styled Flet IconButton with consistent configuration.

Constructs an IconButton with the specified icon, tooltip, click handler,
and optional color. Provides consistent button styling across the application.

## Purpose

- Create standardized icon buttons
        - Ensure consistent button styling
        - Provide accessibility via tooltips
        - Support custom icon colors

## Parameters

- **`icon`** (str): Icon name from Flet's icon set (ft.Icons constants). Examples: ft.Icons.EDIT, ft.Icons.DELETE, ft.Icons.SAVE.
- **`tooltip`** (str): Tooltip text shown on hover. Should describe button action. Examples: "Edit assignment", "Delete file", "Save changes".
- **`on_click`** (Callable): Click event handler function. Signature: (e: ft.ControlEvent) -> None. Called when button clicked.
- **`color`** (ft.Colors, optional): Icon color. If None, uses default theme color. Examples: ft.Colors.RED, ft.Colors.BLUE. Defaults to None.

## Returns

**Type**: `ft.IconButton`


## Algorithm

- 1. **Create Button**:
- a. Instantiate ft.IconButton
- b. Set icon parameter to specified icon
- c. Set tooltip parameter to tooltip text
- d. Set on_click parameter to click handler
- e. Set icon_color parameter to specified color (or None)

- 2. **Return Button**:
- a. Return configured IconButton instance

## Interactions

- **ft.IconButton**: Creates button component

## Example

```python
# Edit button
edit_btn = create_icon_button(
    icon=ft.Icons.EDIT,
    tooltip="Edit assignment",
    on_click=lambda e: edit_assignment(),
    color=ft.Colors.BLUE
    )
page.add(edit_btn)

# Delete button (red)
delete_btn = create_icon_button(
    icon=ft.Icons.DELETE,
    tooltip="Delete file",
    on_click=lambda e: delete_file(),
    color=ft.Colors.RED
    )

# Save button (default color)
save_btn = create_icon_button(
    icon=ft.Icons.SAVE,
    tooltip="Save changes",
    on_click=handle_save
    )
```

## See Also

- `ft.IconButton`: Flet icon button component
- `ft.Icons`: Flet icon constants

## Notes

- Returns configured button (not added to page)
- Tooltip improves accessibility
- Icon color optional (uses theme default if None)
- Click handler receives ControlEvent parameter
- Button can be styled further after creation
- Icons from Material Design icon set
