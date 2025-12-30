---
id: "_create_default_preview"
sidebar_position: 14
title: "_create_default_preview"
---

# ⚙️ _create_default_preview

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`file_preview_service.py`](./file_preview_service.py) | **Line:** 1286
:::

Create generic file preview for unsupported or unknown file types.

Shows format-appropriate icon based on file extension with download
and browser options. Fallback for all unhandled file types.

## Parameters

- **`file_data`** (bytes): File binary content for download.
- **`file_name`** (str): Filename for display, extension detection, and download.
- **`mime_type`** (str or None): MIME type for display. May be None or "Unknown".
- **`size_mb`** (float): File size in megabytes.
- **`file_id`** (str or None): Drive file ID for browser viewing.

## Returns

**Type**: `ft.Column`


## Algorithm

- 1. **Extract Extension**:
    - a. Split filename by '.'
    - b. Get last segment: file_name.split('.')[-1]
    - c. Convert to lowercase
    - d. Store in ext variable
    - e. If no '.', ext = ''

  - 2. **Map Extension to Icon**:
    - a. Define icon_map dictionary:
    - - Archives: 'zip', 'rar', '7z' → (FOLDER_ZIP, PURPLE)
    - - Video: 'mp4', 'avi', 'mov' → (VIDEO_FILE, RED)
    - - Audio: 'mp3', 'wav' → (AUDIO_FILE, BLUE)
    - - Data: 'json' → (DATA_OBJECT, GREEN)
    - - Code: 'xml' → (CODE, ORANGE)
    - - Database: 'sql' → (STORAGE, BLUE)
    - b. Lookup ext in icon_map
    - c. Get (icon, color) tuple
    - d. Default: (INSERT_DRIVE_FILE, GREY) if not found

  - 3. **Build Info Display**:
    - a. Icon with determined icon and color (size 100)
    - b. Title: "File Preview Not Available" (size 20, bold)
    - c. Type display: f"Type: &#123;mime_type or 'Unknown'&#125;" (size 14, grey)
    - d. Size display: f"Size: &#123;size_mb:.2f&#125; MB" (size 14, grey)

  - 4. **Create Action Buttons**:
    - a. Download button: "Download File" → _download_file()
    - b. Open button (if file_id): "Open in Browser" (BLUE) → _open_in_browser()

  - 5. **Layout and Return**:
    - a. Vertical Column layout
    - b. Centered alignment
    - c. 10px spacing

## Interactions

- **str.split()**: Extension extraction
- **_download_file()**: Download handler
- **_open_in_browser()**: Browser opener

## Example

```python
# ZIP file
widget = preview_service._create_default_preview(
    zip_data,
    'archive.zip',
    'application/zip',
    5.0,
    None
    )
# Shows PURPLE folder_zip icon

# Unknown file
widget = preview_service._create_default_preview(
    data,
    'data.custom',
    'application/octet-stream',
    1.0,
    'drive_id'
    )
# Shows generic grey file icon
```

## See Also

- `_render_preview()`: Calls this for unknown types
- `_download_file()`: Download handler

## Notes

- Fallback for all unsupported types
- Extension-based icon selection
- Icon colors match common conventions
- Supports archives, media, code, data files
- Generic file icon for truly unknown types
- Always shows file type and size
- Download available for all types
