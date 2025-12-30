---
id: "show_file_info"
sidebar_position: 13
title: "show_file_info"
---

# ⚙️ show_file_info

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`file_manager.py`](./file_manager.py) | **Line:** 1166
:::

Display file metadata and actions in modal dialog.

Shows comprehensive file information including name, type, size,
and modification date. Provides preview and browser viewing options.
Fetches full metadata if needed.

## Parameters

- **`file`** (dict or str): File metadata dictionary or file ID. If dict, must contain 'id' key for metadata fetch. If full metadata already present, uses directly.

## Returns

**Type**: `None`


## Algorithm

- 1. **Fetch Full Metadata** (if needed):
    - a. Check if file is dict with 'id' key
    - b. If yes:
    - i. Call dash.drive.get_file_info(file["id"])
    - ii. Returns complete metadata
    - iii. Store in info variable
    - c. Else:
    - i. Assume file is already full metadata
    - ii. Use directly as info
    - d. If info is None:
    - i. Fetch failed
    - ii. Return early (no dialog)

  - 2. **Format Size**:
    - a. If info.get('size') exists:
    - i. Call format_file_size(info.get('size'))
    - ii. Converts bytes to readable format
    - b. Else:
    - i. size_str = "N/A" (no size available)

  - 3. **Define Close Handler**:
    - a. Set dialog_container.visible = False
    - b. Call dash.page.update()

  - 4. **Define Preview Handler**:
    - a. Call self.preview_file(info)
    - b. Set dialog_container.visible = False
    - c. Call dash.page.update()
    - d. Closes info, opens preview

  - 5. **Create Action Buttons**:
    - a. Preview button (if service available):
    - i. Text: "Preview"
    - ii. Icon: VISIBILITY
    - iii. on_click: on_preview
    - b. Browser button (always):
    - i. Text: "Open in Browser"
    - ii. Icon: OPEN_IN_NEW
    - iii. on_click: lambda → open_drive_file(info.get('id'))

  - 6. **Build Dialog UI**:
    - a. Create dialog_container:
    - i. Title: "File Information" (size 20, bold)
    - ii. Metadata fields:
    - - Name: info.get('name', 'N/A')
    - - Type: info.get('mimeType', 'N/A')
    - - Size: size_str
    - - Modified: info.get('modifiedTime', 'N/A')[:10]
    - iii. Divider separator
    - iv. Action Row: preview + browser buttons
    - v. Close button Row
    - vi. Width: 400px, white background, rounded

  - 7. **Show Dialog**:
    - a. Append to dash.page.overlay
    - b. Call dash.page.update()

## Interactions

- **DriveService.get_file_info()**: Metadata fetch
- **format_file_size()**: Size formatting
- **open_drive_file()**: Browser opening
- **preview_file()**: Preview display
- **ft.Container**: Dialog structure

## Example

```python
# Show info with partial metadata
file = {'id': 'file_123', 'name': 'document.pdf'}
file_manager.show_file_info(file)
# Fetches full metadata from Drive
# Dialog shows:
# Name: document.pdf
# Type: application/pdf
# Size: 2.5 MB
# Modified: 2024-01-15
# [Preview] [Open in Browser] [Close]

# Show info with full metadata
full_file = {
    'id': 'file_456',
    'name': 'report.docx',
    'mimeType': 'application/vnd.openxmlformats...',
    'size': '1048576',
    'modifiedTime': '2024-02-20T10:30:00.000Z'
    }
file_manager.show_file_info(full_file)
# Uses metadata directly (no fetch)

# Click Preview button
# → Closes info dialog
# → Opens preview overlay

# Click Open in Browser
# → Opens file in Drive web viewer
```

## See Also

- `show_menu()`: Includes info option
- `preview_file()`: Preview handler
- `format_file_size()`: Size formatter
- `open_drive_file()`: Browser opener

## Notes

- Fetches full metadata if partial provided
- Shows comprehensive file information
- Preview option if service available
- Browser viewing always available
- Modified date truncated to date only ([:10])
- Size formatted for readability
- N/A shown for missing fields
- Modal blocks interaction
- Divider separates info from actions
