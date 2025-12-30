---
id: "create_folder_item"
sidebar_position: 5
title: "create_folder_item"
---

# ⚙️ create_folder_item

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`file_manager.py`](./file_manager.py) | **Line:** 348
:::

Create visual folder list item with icon, name, count, and menu.

Generates styled Container representing folder in file list. Includes
folder icon, display name (truncated if long), subfolder count, and
context menu. Click opens folder contents.

## Parameters

- **`folder`** (dict): Folder metadata dictionary. Must contain: - 'name' (str): Folder display name - 'id' (str): Folder Drive ID May contain additional metadata keys.
- **`subfolder_count`** (int): Number of subfolders within this folder. Displayed as "&#123;count&#125; folders" text. May be 0.
- **`is_shared_drive`** (bool, optional): Whether folder is shared drive root. Passed to open_folder and show_menu. Defaults to False.

## Returns

**Type**: `ft.Container`

                - Folder icon (24px)
                - Column with name and subfolder count
                - PopupMenuButton with context menu
                Has bottom border, padding, and click handler.

## Algorithm

- 1. **Extract and Format Name**:
    - a. Get folder name: folder.get("name", "Untitled")
    - b. If length > 40 characters:
    - i. Truncate to 37 chars
    - ii. Append "..." (ellipsis)
    - iii. Store in display_name
    - c. Else: display_name = folder_name as-is

  - 2. **Generate Context Menu**:
    - a. Call self.show_menu(folder, is_folder=True, is_shared_drive)
    - b. Returns list of PopupMenuItem objects
    - c. Store in menu_items

  - 3. **Build UI Structure**:
    - a. Create ft.Row with components:
    - i. ft.Icon(FOLDER, size=24)
    - ii. ft.Column(expand=True):
    - - ft.Text(display_name, size=14)
    - - ft.Text(f"&#123;subfolder_count&#125; folders", size=12, grey)
    - iii. ft.PopupMenuButton(items=menu_items)

  - 4. **Wrap in Container**:
    - a. Set content to Row
    - b. Set padding: 10px
    - c. Set border: bottom only, 1px grey
    - d. Register on_click handler:
    - i. Lambda captures folder reference
    - ii. Calls self.open_folder(folder, is_shared_drive)

  - 5. **Return Container**:
    - a. Return styled, clickable folder item

## Interactions

- **show_menu()**: Generates context menu
- **open_folder()**: Click handler
- **ft.Container, ft.Row, ft.Column**: Layout
- **ft.Icon, ft.Text**: Visual elements
- **ft.PopupMenuButton**: Menu display

## Example

```python
# Create folder item
folder = {
    'id': 'folder_abc123',
    'name': 'My Documents',
    'mimeType': 'application/vnd.google-apps.folder'
    }
item = file_manager.create_folder_item(folder, subfolder_count=5)
dashboard.folder_list.controls.append(item)

# Long name truncation
long_folder = {
    'id': 'folder_xyz',
    'name': 'This is a very long folder name that exceeds forty characters'
    }
item = file_manager.create_folder_item(long_folder, 0)
# Display shows: "This is a very long folder name th..."

# Shared drive folder
shared = {'id': 'shared_123', 'name': 'Team Drive'}
item = file_manager.create_folder_item(
    shared,
    subfolder_count=10,
    is_shared_drive=True
    )
```

## See Also

- `show_menu()`: Context menu generation
- `open_folder()`: Click handler
- `create_file_item()`: Similar for files

## Notes

- Name truncated at 40 characters (37 + "...")
- Subfolder count informational only
- Click opens folder contents (navigates)
- Context menu via three-dot button
- Bottom border separates list items
- Icon always folder icon (not dynamic)
- is_shared_drive affects navigation behavior
