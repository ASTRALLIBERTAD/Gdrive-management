---
id: "preview_file"
sidebar_position: 7
title: "preview_file"
---

# ⚙️ preview_file

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`file_manager.py`](./file_manager.py) | **Line:** 633
:::

Open file preview overlay for supported file types.

Initiates FilePreviewService to display file in modal overlay.
Checks for service availability and ensures item is not a folder
before attempting preview.

## Parameters

- **`file`** (dict): File metadata dictionary containing: - 'id' (str): File Drive ID for fetching content - 'name' (str): File name for display - 'mimeType' (str): Used to check if folder Additional metadata may be present.

## Returns

**Type**: `None`


## Algorithm

- 1. **Check Preview Service**:
    - a. If self.file_preview is None:
    - i. Service not available
    - ii. Return early (no preview)

  - 2. **Check Item Type**:
    - a. Get mimeType: file.get("mimeType")
    - b. If mimeType == "application/vnd.google-apps.folder":
    - i. Item is folder (cannot preview)
    - ii. Return early

  - 3. **Open Preview**:
    - a. Call file_preview.show_preview() with:
    - i. file_id: file.get("id")
    - ii. file_name: file.get("name", "File")
    - b. Service handles:
    - i. File download from Drive
    - ii. Format detection
    - iii. Preview rendering
    - iv. Modal overlay display

## Interactions

- **FilePreviewService.show_preview()**: Opens preview
- **DriveService**: (via preview service) Downloads file

## Example

```python
# Preview PDF file
pdf_file = {
    'id': 'file_abc123',
    'name': 'document.pdf',
    'mimeType': 'application/pdf'
    }
file_manager.preview_file(pdf_file)
# Modal overlay opens with PDF preview

# Preview image
image = {
    'id': 'img_xyz',
    'name': 'photo.jpg',
    'mimeType': 'image/jpeg'
    }
file_manager.preview_file(image)
# Image displayed inline in overlay

# Attempt folder preview (no-op)
folder = {
    'id': 'folder_123',
    'name': 'Documents',
    'mimeType': 'application/vnd.google-apps.folder'
    }
file_manager.preview_file(folder)
# Nothing happens (returns early)

# No preview service (no-op)
file_manager.file_preview = None
file_manager.preview_file(pdf_file)
# Nothing happens (returns early)
```

## See Also

- `FilePreviewService`: Preview service
- `create_file_item()`: Adds preview button
- `show_menu()`: Includes preview in menu

## Notes

- Checks both service availability and item type
- Folders cannot be previewed (early return)
- Service handles all preview logic
- Modal overlay blocks interaction
- Supports images, text, PDFs, Office docs
- No error raised if service unavailable
- Preview service downloads file from Drive
