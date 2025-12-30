---
id: "show_preview"
sidebar_position: 4
title: "show_preview"
---

# ⚙️ show_preview

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`file_preview_service.py`](./file_preview_service.py) | **Line:** 235
:::

Display file preview in modal overlay with loading state.

Creates and displays a modal overlay containing file preview. Handles
asynchronous loading from Drive or local filesystem with progress indicator.
Shows file header with close button and preview content area.

## Parameters

- **`file_id`** (str, optional): Google Drive file ID for Drive-hosted files. 33-character alphanumeric string. Requires drive_service to be set. If provided, file loaded via Drive API. Defaults to None.
- **`file_path`** (str, optional): Absolute or relative path to local file. File must exist and be readable. Used when file_id not provided. Defaults to None.
- **`file_name`** (str, optional): Display name for file in overlay header. Shown with visibility icon. Can be descriptive name even if different from actual filename. Defaults to "File".

## Returns

**Type**: `None`

                displayed asynchronously after file loads.

## Algorithm

- 1. **Create Loading Container**:
    - a. Build ft.Container with centered Column
    - b. Add ProgressRing for loading animation
    - c. Add "Loading preview..." text
    - d. Set container size: 700x500
    - e. Center alignment for progress indicator

  - 2. **Define Close Handler**:
    - a. Create close_preview(e) function
    - b. Implementation:
    - i. Check if current_overlay exists and in page.overlay
    - ii. Remove overlay from page.overlay
    - iii. Set current_overlay = None
    - iv. Call page.update()

  - 3. **Build Overlay Structure**:
    - a. Create header Row with:
    - i. Visibility icon (BLUE)
    - ii. File name text (size 18, bold, expandable)
    - iii. Close IconButton (calls close_preview)
    - b. Add Divider separator
    - c. Add content_container (loading initially)
    - d. Wrap in Column (tight spacing)

  - 4. **Style Overlay Container**:
    - a. Set padding: 20px
    - b. Set bgcolor: WHITE
    - c. Set border_radius: 10px
    - d. Set dimensions: 750x600
    - e. Add shadow effect (blur 20, opacity 0.3)

  - 5. **Create Modal Background**:
    - a. Center inner container
    - b. Set expand: True (full screen)
    - c. Set backdrop: semi-transparent BLACK (opacity 0.5)
    - d. Prevent click-through (on_click: lambda e: None)

  - 6. **Display Overlay**:
    - a. Append overlay to page.overlay list
    - b. Store in self.current_overlay
    - c. Call page.update() to render

  - 7. **Route to Loader**:
    - a. If file_id provided AND drive_service exists:
    - i. Call _load_from_drive() with parameters
    - ii. Async load from Drive
    - b. Elif file_path provided:
    - i. Call _load_from_path() with parameters
    - ii. Sync load from filesystem
    - c. Else (neither provided):
    - i. Update content_container with error
    - ii. Show "No file to preview" message with error icon
    - iii. Call page.update()

## Interactions

- **ft.Container, ft.Column, ft.Row**: UI structure
- **ft.ProgressRing**: Loading indicator
- **ft.IconButton**: Close button
- **page.overlay**: Modal display
- **_load_from_drive()**: Drive file loading
- **_load_from_path()**: Local file loading

## Example

```python
# Preview Drive file
preview_service.show_preview(
    file_id='1abc...xyz',
    file_name='Assignment.pdf'
    )
# Overlay shows with loading spinner
# Then PDF preview or placeholder

# Preview local file
preview_service.show_preview(
    file_path='C:/docs/report.txt',
    file_name='Report'
    )

# Error case (no file specified)
preview_service.show_preview(file_name='Unknown')
# Shows "No file to preview" error
```

## See Also

- `_load_from_drive()`: Drive file loading
- `_load_from_path()`: Local file loading
- `close_preview()`: Close overlay programmatically

## Notes

- Loading state shown immediately
- Actual preview loaded asynchronously
- Close button always available
- Modal blocks page interaction
- Backdrop click does not close (explicit close required)
- Overlay sized for typical documents (750x600)
- Content container updated when file loads
