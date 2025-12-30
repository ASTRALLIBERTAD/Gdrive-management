---
id: "create_file_item"
sidebar_position: 6
title: "create_file_item"
---

# ⚙️ create_file_item

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`file_manager.py`](./file_manager.py) | **Line:** 475
:::

Create visual file list item with icon, name, size, and actions.

Generates styled Container representing file in list. Includes appropriate
icon, file name, size display, preview button (if available), and context
menu. Click opens file preview.

## Parameters

- **`file`** (dict): File metadata dictionary. Should contain: - 'id' (str): File Drive ID - 'name' (str): File display name - 'mimeType' (str): File MIME type - 'size' (str or int, optional): File size in bytes Additional metadata keys may be present.

## Returns

**Type**: `ft.Container`

                - File/folder icon (24px)
                - Column with name and size
                - Preview button (if file and service available)
                - PopupMenuButton with context menu
                Has bottom border, padding, and click handler.

## Algorithm

- 1. **Determine Item Type**:
    - a. Check mimeType: file.get("mimeType")
    - b. Set is_folder = (mimeType == "application/vnd.google-apps.folder")
    - c. Handles rare case of folder in file list

  - 2. **Select Icon and Size**:
    - a. If is_folder:
    - i. icon = ft.Icons.FOLDER
    - ii. size_str = "Folder"
    - b. Else (regular file):
    - i. icon = ft.Icons.INSERT_DRIVE_FILE
    - ii. size_str = format_file_size(file.get("size"))
    - iii. Formats bytes to human-readable (KB, MB, etc.)

  - 3. **Generate Context Menu**:
    - a. Call self.show_menu(file, is_folder=is_folder)
    - b. Returns list of PopupMenuItem objects

  - 4. **Build Action Buttons**:
    - a. Initialize empty list: action_buttons
    - b. If not folder AND preview service exists:
    - i. Create preview icon button:
    - - Icon: VISIBILITY
    - - Tooltip: "Preview"
    - - on_click: lambda captures file, calls preview_file
    - ii. Append to action_buttons
    - c. Always append PopupMenuButton(items=menu_items)

  - 5. **Build UI Structure**:
    - a. Create ft.Row with:
    - i. ft.Icon(icon, size=24)
    - ii. ft.Column(expand=True):
    - - ft.Text(file.get("name", "Untitled"), size=14)
    - - ft.Text(size_str, size=12, grey)
    - iii. *action_buttons (unpacked list)

  - 6. **Wrap in Container**:
    - a. Set content to Row
    - b. Set padding: 10px
    - c. Set border: bottom only, 1px light grey
    - d. Register on_click handler:
    - i. If folder: lambda calls handle_file_click(file)
    - ii. If file: lambda calls preview_file(file)

  - 7. **Return Container**:
    - a. Return styled, clickable file item

## Interactions

- **show_menu()**: Context menu generation
- **preview_file()**: Preview handler
- **handle_file_click()**: Folder navigation
- **format_file_size()**: Size formatting (utils.common)
- **create_icon_button()**: Button helper (utils.common)
- **ft.Container, ft.Row, ft.Column**: Layout

## Example

```python
# Regular file
file = {
    'id': 'file_123',
    'name': 'report.pdf',
    'mimeType': 'application/pdf',
    'size': '2048576'  # 2MB
    }
item = file_manager.create_file_item(file)
# Shows: PDF icon, "report.pdf", "2.00 MB", preview + menu

# Image file
image = {
    'id': 'img_456',
    'name': 'photo.jpg',
    'mimeType': 'image/jpeg',
    'size': '1048576'  # 1MB
    }
item = file_manager.create_file_item(image)
# Click opens image preview

# Folder in file list (edge case)
folder = {
    'id': 'folder_789',
    'name': 'Subfolder',
    'mimeType': 'application/vnd.google-apps.folder'
    }
item = file_manager.create_file_item(folder)
# Shows folder icon, "Folder", no preview button
# Click navigates to folder
```

## See Also

- `show_menu()`: Context menu
- `preview_file()`: Preview handler
- `handle_file_click()`: Folder handler
- `format_file_size()`: Size formatter
- `create_icon_button()`: Button helper

## Notes

- Handles both files and folders (edge case)
- Preview button only for files with service
- Size formatted for readability
- Generic file icon (not MIME-specific)
- Click behavior differs: folder → navigate, file → preview
- Action buttons list allows flexible additions
- Bottom border lighter than folder items (visual hierarchy)
