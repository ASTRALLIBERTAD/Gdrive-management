---
id: "open_folder"
sidebar_position: 8
title: "open_folder"
---

# ⚙️ open_folder

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`file_manager.py`](./file_manager.py) | **Line:** 729
:::

Navigate Dashboard to display folder contents.

Triggers Dashboard to change current view to specified folder,
loading and displaying its contents. Updates breadcrumb navigation.

## Parameters

- **`folder`** (dict): Folder metadata dictionary containing: - 'id' (str): Folder Drive ID for content fetching - 'name' (str, optional): Folder name for breadcrumb Additional metadata may be present.
- **`is_shared_drive`** (bool, optional): Whether folder is within shared drive. Affects navigation and permissions. Defaults to False.

## Returns

**Type**: `None`


## Algorithm

- 1. **Extract Folder Info**:
    - a. Get folder ID: folder["id"]
    - b. Get folder name: folder.get("name", folder["id"])
    - c. Use ID as fallback if name missing

  - 2. **Trigger Navigation**:
    - a. Call dash.show_folder_contents() with:
    - i. folder_id: extracted ID
    - ii. folder_name: extracted name
    - iii. is_shared_drive: flag parameter
    - b. Dashboard handles:
    - i. Fetching folder contents from Drive
    - ii. Updating current_folder_id state
    - iii. Refreshing file list display
    - iv. Updating breadcrumb navigation

## Interactions

- **Dashboard.show_folder_contents()**: Navigation method
- **DriveService**: (via Dashboard) Fetches contents

## Example

```python
# Navigate to folder
folder = {
    'id': 'folder_abc123',
    'name': 'Documents',
    'mimeType': 'application/vnd.google-apps.folder'
    }
file_manager.open_folder(folder)
# Dashboard displays Documents folder contents

# Shared drive folder
shared_folder = {
    'id': 'shared_xyz',
    'name': 'Team Drive'
    }
file_manager.open_folder(shared_folder, is_shared_drive=True)

# Folder without name (uses ID)
minimal_folder = {'id': 'folder_123'}
file_manager.open_folder(minimal_folder)
# Breadcrumb shows folder_123
```

## See Also

- `show_folder_contents()`: Navigation handler
- `handle_file_click()`: Routes folder clicks here
- `create_folder_item()`: Adds click handler

## Notes

- Called from folder item click handler
- Dashboard manages navigation state
- Breadcrumb updated automatically
- Contents fetched from Drive API
- is_shared_drive affects permissions
- Name fallback to ID if missing
