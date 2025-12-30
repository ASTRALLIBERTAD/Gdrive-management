---
id: "handle_file_click"
sidebar_position: 9
title: "handle_file_click"
---

# ⚙️ handle_file_click

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`file_manager.py`](./file_manager.py) | **Line:** 804
:::

Route file click to appropriate handler based on type.

Determines whether clicked item is folder or file and routes to
appropriate action: navigation for folders, preview for files.

## Parameters

- **`file`** (dict): File or folder metadata dictionary containing: - 'mimeType' (str): Used to determine type - 'id' (str): For navigation or preview - 'name' (str): For display Additional metadata may be present.

## Returns

**Type**: `None`


## Algorithm

- 1. **Check MIME Type**:
    - a. Get mimeType: file.get("mimeType")
    - b. Compare to folder MIME type

  - 2. **Route to Handler**:
    - a. If mimeType == "application/vnd.google-apps.folder":
    - i. Call dash.show_folder_contents() with:
    - - file["id"]
    - - file["name"]
    - ii. Navigates to folder
    - b. Else (regular file):
    - i. Call self.preview_file(file)
    - ii. Opens preview overlay

## Interactions

- **Dashboard.show_folder_contents()**: Folder navigation
- **preview_file()**: File preview

## Example

```python
# Click folder
folder = {
    'id': 'folder_123',
    'name': 'Documents',
    'mimeType': 'application/vnd.google-apps.folder'
    }
file_manager.handle_file_click(folder)
# Navigates to Documents folder

# Click file
file = {
    'id': 'file_456',
    'name': 'report.pdf',
    'mimeType': 'application/pdf'
    }
file_manager.handle_file_click(file)
# Opens PDF preview
```

## See Also

- `preview_file()`: File preview handler
- `show_folder_contents()`: Folder handler

## Notes

- Simple router based on MIME type
- Folders navigate, files preview
- Used in create_file_item click handler
- MIME type reliable for type detection
