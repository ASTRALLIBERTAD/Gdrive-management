---
id: "show_overlay"
sidebar_position: 14
title: "show_overlay"
---

# ⚙️ show_overlay

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`todo_view.py`](./todo_view.py) | **Line:** 1337
:::

Display a modal overlay dialog with custom content.

Creates and shows a centered modal dialog containing the provided
content control. Supports custom title, dimensions, and scrollable
content. Returns both the overlay control and a close function.

## Parameters

- **`content`** (ft.Control): The primary content widget to display in dialog body. Can be any Flet control (Column, Container, etc.).
- **`title`** (str, optional): Title text displayed in dialog header. If None, no title shown. Defaults to None.
- **`width`** (int, optional): Dialog width in pixels. Defaults to 400.
- **`height`** (int, optional): Dialog height in pixels. If provided and content is scrollable Column, wraps content in container with height constraint. Defaults to None (auto-height).

## Returns

**Type**: `tuple`

                - overlay (ft.Container): The overlay control added to page.
                - close_overlay (Callable): Function to close the overlay.
                  Signature: (e) -> None. Call with None or event object.

## Algorithm

- 1. **Define Close Function**:
    - a. Create close_overlay(e) function
    - b. Implementation:
    - i. Check if overlay in page.overlay list
    - ii. If present, remove overlay
    - iii. Call page.update()

  - 2. **Build Header Controls**:
    - a. Create empty list header_controls
    - b. If title provided:
    - i. Create Text with title, size 20, bold
    - ii. Set overflow VISIBLE, no_wrap False, expand True
    - iii. Append to header_controls
    - c. Create IconButton with CLOSE icon
    - d. Set on_click to close_overlay
    - e. Append close button to header_controls

  - 3. **Wrap Content** (if height specified):
    - a. If height AND content is scrollable Column:
    - i. Wrap content in Container
    - ii. Set expand=True, padding=10
    - iii. Store in content_wrapper
    - b. Else:
    - i. Use content as-is (content_wrapper = content)

  - 4. **Build Overlay Content**:
    - a. Create Column with:
    - i. Row(header_controls) - title and close button
    - ii. Divider - separator line
    - iii. content_wrapper - main content
    - b. Set tight=True, spacing=10
    - c. Set expand=True if height specified

  - 5. **Build Inner Container**:
    - a. Create Container with:
    - i. content=overlay_content
    - ii. padding=20, bgcolor=WHITE
    - iii. border_radius=10
    - iv. width=width, height=height (if specified)
    - v. shadow with blur_radius=20

  - 6. **Build Outer Overlay**:
    - a. Create Container with:
    - i. content=inner_container
    - ii. alignment=center
    - iii. expand=True
    - iv. bgcolor=semi-transparent black (0.5 opacity)
    - v. on_click=lambda e: None (prevents click-through)

  - 7. **Display Overlay**:
    - a. Append overlay to page.overlay list
    - b. Call page.update()

  - 8. **Return Tuple**:
    - a. Return (overlay, close_overlay)
    - b. Caller can close by calling close_overlay(None)

## Interactions

- **ft.Container**: Creates overlay structure
- **ft.Column, ft.Row**: Arranges header and content
- **ft.Text, ft.IconButton**: Header components
- **ft.Page.overlay**: Adds/removes overlay

## Example

```python
# Simple dialog
content = ft.Column([
    ft.Text("Are you sure?"),
    ft.Row([
    ft.TextButton("Cancel", on_click=lambda e: close_fn(e)),
    ft.ElevatedButton("Confirm", on_click=handle_confirm)
    ])
    ])
overlay, close_fn = todo_view.show_overlay(
    content,
    title="Confirm Delete",
    width=300
    )

# Scrollable dialog with height
long_content = ft.Column([...], scroll="auto")
overlay, close_fn = todo_view.show_overlay(
    long_content,
    title="View Details",
    width=500,
    height=600
    )

# Close dialog programmatically
close_fn(None)
```

## See Also

- `show_snackbar()`: Alternative for brief notifications
- `AssignmentManager`: Uses this for dialogs
- `StudentManager`: Uses this for dialogs

## Notes

- Modal overlay blocks interaction with page content
- Semi-transparent black background (50% opacity)
- Close button always shown in header
- Content can be any Flet control
- Scrollable columns automatically wrapped if height specified
- Shadow effect adds depth to dialog
- Click on overlay background doesn't close (must use close button)
- Multiple overlays can be shown (stacked)
