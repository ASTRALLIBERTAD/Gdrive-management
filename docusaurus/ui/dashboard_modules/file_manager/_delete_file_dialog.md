---
id: "_delete_file_dialog"
sidebar_position: 12
title: "_delete_file_dialog"
---

# ⚙️ _delete_file_dialog

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`file_manager.py`](./file_manager.py) | **Line:** 1032
:::

Display confirmation dialog for file or folder deletion.

Shows modal dialog with warning message and item name. User must
confirm deletion before API call. On confirm, deletes from Drive
and refreshes Dashboard.

## Parameters

- **`file`** (dict): File or folder metadata containing: - 'id' (str): Item ID for deletion - 'name' (str): Item name for confirmation message Additional metadata may be present.

## Returns

**Type**: `None`


## Algorithm

- 1. **Define Delete Handler**:
    - a. Call API:
    - i. dash.drive.delete_file(file["id"])
    - ii. Permanently deletes from Drive
    - b. Refresh UI:
    - i. dash.refresh_folder_contents()
    - ii. Removes item from display
    - c. Close dialog:
    - i. Set dialog_container.visible = False
    - ii. Call dash.page.update()

  - 2. **Define Cancel Handler**:
    - a. Set dialog_container.visible = False
    - b. Call dash.page.update()
    - c. No deletion (safe exit)

  - 3. **Build Dialog UI**:
    - a. Create dialog_container:
    - i. Outer: Semi-transparent backdrop
    - ii. Inner: White container with:
    - - Title: "Confirm Delete" (size 20, bold)
    - - Warning: "Delete '&#123;name&#125;'?" (file name)
    - - Action Row:
    - - Cancel button (TextButton)
    - - Delete button (ElevatedButton, RED)
    - iii. Centered alignment
    - iv. Width: 400px

  - 4. **Show Dialog**:
    - a. Append to dash.page.overlay
    - b. Call dash.page.update()
    - c. Wait for user interaction

## Interactions

- **DriveService.delete_file()**: API delete operation
- **Dashboard.refresh_folder_contents()**: UI refresh
- **ft.Container**: Dialog structure
- **dash.page.overlay**: Modal display

## Example

```python
# Delete file with confirmation
file = {
    'id': 'file_123',
    'name': 'document.pdf',
    'mimeType': 'application/pdf'
    }
file_manager._delete_file_dialog(file)
# Dialog: "Delete 'document.pdf'?"
# User clicks Delete (RED button)
# → Drive API: delete_file('file_123')
# → Dashboard refreshes
# → File removed from display
# → Dialog closes

# Cancel deletion
file_manager._delete_file_dialog(file)
# User clicks Cancel
# → Dialog closes
# → No API call, file preserved

# Delete folder (recursive)
folder = {
    'id': 'folder_456',
    'name': 'Old Folder'
    }
file_manager._delete_file_dialog(folder)
# Deletes folder and all contents
```

## See Also

- `show_menu()`: Includes delete option
- `delete_file()`: API method
- `refresh_folder_contents()`: Refresh

## Notes

- Confirmation required (safety measure)
- Shows item name for clarity
- Delete button RED (danger indicator)
- Refreshes Dashboard after deletion
- Permanent deletion (not trash)
- Modal blocks interactions
- Works for files and folders
- Folder deletion is recursive
