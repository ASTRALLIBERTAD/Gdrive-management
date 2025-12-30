---
id: "_rename_file_dialog"
sidebar_position: 11
title: "_rename_file_dialog"
---

# ⚙️ _rename_file_dialog

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`file_manager.py`](./file_manager.py) | **Line:** 896
:::

Display modal dialog for renaming file or folder.

Shows overlay dialog with text input pre-filled with current name.
User can modify name and confirm or cancel. On confirm, updates
file via Drive API and refreshes Dashboard.

## Parameters

- **`file`** (dict): File or folder metadata containing: - 'id' (str): Item ID for rename operation - 'name' (str): Current name for pre-fill Additional metadata may be present but not used.

## Returns

**Type**: `None`


## Algorithm

- 1. **Create Input Field**:
    - a. Create ft.TextField with:
    - i. value: file["name"] (pre-filled)
    - ii. autofocus: True (cursor ready)

  - 2. **Define Rename Handler**:
    - a. Get new name: name_field.value.strip()
    - b. Validate input:
    - i. If empty, return (no-op)
    - ii. If unchanged, return (no-op)
    - c. Call API:
    - i. dash.drive.rename_file(file["id"], new_name)
    - ii. Updates file in Drive
    - d. Refresh UI:
    - i. dash.refresh_folder_contents()
    - ii. Fetches updated file list
    - e. Close dialog:
    - i. Set dialog_container.visible = False
    - ii. Call dash.page.update()

  - 3. **Define Cancel Handler**:
    - a. Set dialog_container.visible = False
    - b. Call dash.page.update()
    - c. No API call (discard changes)

  - 4. **Build Dialog UI**:
    - a. Create dialog_container (ft.Container):
    - i. Outer: Semi-transparent black backdrop
    - ii. Inner: White container with:
    - - Title: "Rename" (size 20, bold)
    - - Input field (name_field)
    - - Action Row:
    - - Cancel button (TextButton)
    - - Rename button (ElevatedButton)
    - iii. Centered alignment
    - iv. Width: 400px

  - 5. **Show Dialog**:
    - a. Append dialog_container to dash.page.overlay
    - b. Call dash.page.update() to render
    - c. User interacts with modal

## Interactions

- **DriveService.rename_file()**: API rename operation
- **Dashboard.refresh_folder_contents()**: UI refresh
- **ft.TextField**: Input control
- **ft.Container**: Dialog structure
- **dash.page.overlay**: Modal display

## Example

```python
# Rename file
file = {
    'id': 'file_123',
    'name': 'old_name.pdf',
    'mimeType': 'application/pdf'
    }
file_manager._rename_file_dialog(file)
# Dialog appears with "old_name.pdf" in input
# User changes to "new_name.pdf" and clicks Rename
# → Drive API called: rename_file('file_123', 'new_name.pdf')
# → Dashboard refreshes to show new name
# → Dialog closes

# Cancel rename
file_manager._rename_file_dialog(file)
# User clicks Cancel
# → Dialog closes
# → No API call, no changes
```

## See Also

- `show_menu()`: Includes rename option
- `rename_file()`: API method
- `refresh_folder_contents()`: Refresh

## Notes

- Pre-fills current name for editing
- Validates non-empty and changed
- Refreshes Dashboard after rename
- Modal blocks other interactions
- Cancel discards changes (no API call)
- Overlay system for modal behavior
- Works for both files and folders
