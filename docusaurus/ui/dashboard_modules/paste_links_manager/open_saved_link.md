---
id: "open_saved_link"
sidebar_position: 8
title: "open_saved_link"
---

# ⚙️ open_saved_link

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`paste_links_manager.py`](./paste_links_manager.py) | **Line:** 637
:::

Open saved Drive link (navigate folder or preview file).

Routes saved link to appropriate handler based on type: navigates
to folder contents or opens file preview/info dialog.

## Parameters

- **`item`** (dict): Saved link item containing: - 'id' (str): Drive file or folder ID - 'name' (str): Display name - 'mimeType' (str): MIME type for routing Additional keys may be present.

## Returns

**Type**: `None`


## Algorithm

- 1. **Check Item Type**:
    - a. Get mimeType: item.get("mimeType")
    - b. Compare to folder MIME type

  - 2. **Handle Folder**:
    - a. If mimeType == "application/vnd.google-apps.folder":
    - i. Extract folder ID: item["id"]
    - ii. Extract name: item.get("name", item["id"]) (fallback)
    - iii. Call dash.folder_navigator.show_folder_contents():
    - - folder_id: extracted ID
    - - folder_name: extracted name
    - iv. Navigates to folder view
    - v. Return (routing complete)

  - 3. **Handle File** (else branch):
    - a. Check if preview service available
    - b. If self.file_preview exists:
    - i. Call file_preview.show_preview() with:
    - - file_id: item["id"]
    - - file_name: item.get("name", "File")
    - ii. Opens preview modal
    - c. Else (no preview service):
    - i. Fetch full info: dash.drive.get_file_info(item["id"])
    - ii. If info retrieved:
    - - Call dash.file_manager.show_file_info(info)
    - - Shows metadata dialog
    - iii. If info fetch failed:
    - - Create error snackbar
    - - Message: "Failed to open saved link"
    - - Set open=True
    - - Assign to dash.page.snack_bar
    - - Call dash.page.update()

## Interactions

- **FolderNavigator.show_folder_contents()**: Folder navigation
- **FilePreviewService.show_preview()**: File preview
- **DriveService.get_file_info()**: Metadata fetch
- **FileManager.show_file_info()**: Info dialog
- **ft.SnackBar**: Error feedback

## Example

```python
# Open folder link
folder_item = {
    'id': 'abc123',
    'name': 'Project Files',
    'mimeType': 'application/vnd.google-apps.folder'
    }
paste_manager.open_saved_link(folder_item)
# Navigates to folder contents

# Open file link (with preview)
file_item = {
    'id': 'xyz789',
    'name': 'Report.pdf',
    'mimeType': 'application/pdf'
    }
paste_manager.open_saved_link(file_item)
# Opens PDF preview modal

# Open file (no preview service)
paste_manager.file_preview = None
paste_manager.open_saved_link(file_item)
# Fetches info and shows metadata dialog

# Error case (file not accessible)
paste_manager.open_saved_link(file_item)
# Shows: "Failed to open saved link" snackbar
```

## See Also

- `show_folder_contents()`: Folder handler
- `show_preview()`: Preview display
- `show_file_info()`: Info fallback

## Notes

- Routing by MIME type
- Folders always navigable
- Files preview or show info
- Graceful degradation without preview
- Error snackbar on fetch failure
- Called from saved link UI clicks
