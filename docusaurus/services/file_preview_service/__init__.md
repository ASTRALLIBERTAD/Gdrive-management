---
id: "__init__"
sidebar_position: 3
title: "__init__"
---

# 🔧 __init__

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`file_preview_service.py`](./file_preview_service.py) | **Line:** 180
:::

Initialize FilePreviewService with page and optional Drive service.

Sets up the preview service with UI context and file access capabilities.
Prepares for displaying previews without creating any UI elements yet.

## Parameters

- **`page`** (ft.Page): Flet page instance for displaying overlays and managing UI updates. Must be active and rendered. Provides access to page.overlay list for modal display.
- **`drive_service`** (DriveService, optional): Google Drive service wrapper for fetching Drive-hosted files. If None, only local file preview available. Must be authenticated if provided. Defaults to None.

## Algorithm

- 1. **Store Page Reference**:
    - a. Assign page parameter to self.page
    - b. Used for overlay management and UI updates

  - 2. **Store Drive Service**:
    - a. Assign drive_service to self.drive_service
    - b. May be None if Drive integration unavailable

  - 3. **Initialize Overlay State**:
    - a. Set self.current_overlay = None
    - b. No preview active initially
    - c. Updated when preview displayed

## Interactions

- **ft.Page**: Stored for overlay and update operations

## Example

```python
# With Drive service
auth = GoogleAuth()
drive = DriveService(auth.get_service())
preview = FilePreviewService(page, drive)

# Without Drive service (local files only)
preview = FilePreviewService(page)
preview.show_preview(file_path='local.txt', file_name='local.txt')
```

## See Also

- `show_preview()`: Display file preview
- `DriveService`: Drive file access

## Notes

- No UI created during initialization
- current_overlay starts as None
- drive_service optional (local files work without it)
- Page must be active for overlay display
