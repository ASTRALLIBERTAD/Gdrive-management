---
id: "_create_error_view"
sidebar_position: 15
title: "_create_error_view"
---

# ⚙️ _create_error_view

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`file_preview_service.py`](./file_preview_service.py) | **Line:** 1415
:::

Create error message widget for failed file loading.

Displays user-friendly error state when file cannot be loaded.
Provides fallback browser option if Drive file.

## Parameters

- **`error_message`** (str): Error description to display. Should be user-friendly and concise. Example: "Error loading file: File not found"
- **`file_id`** (str, optional): Drive file ID for fallback browser viewing. If provided, shows "Open in Browser" button. Defaults to None.

## Returns

**Type**: `ft.Column`


## Algorithm

- 1. **Build Error Display**:
    - a. RED ERROR icon (size 48)
    - b. Error message text (RED, center-aligned)

  - 2. **Add Fallback Action** (if file_id):
    - a. Add 20px spacing Container
    - b. Add "Open in Browser" button:
    - i. Icon: OPEN_IN_NEW
    - ii. on_click: lambda e: _open_in_browser(file_id)

  - 3. **Layout and Return**:
    - a. Vertical Column layout
    - b. Centered alignment

## Interactions

- **_open_in_browser()**: Fallback browser viewing

## Example

```python
# Drive file error with fallback
widget = preview_service._create_error_view(
    "Error loading file: Permission denied",
    file_id='drive_id'
    )
# Shows error with browser button

# Local file error (no fallback)
widget = preview_service._create_error_view(
    "Error loading file: File not found"
    )
# Shows error only
```

## See Also

- `_load_from_drive()`: Uses this on errors
- `_load_from_path()`: Uses this on errors

## Notes

- User-friendly error display
- RED icon and text (clear error indication)
- Browser fallback for Drive files only
- No fallback for local file errors
- Error message should be concise
