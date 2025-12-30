---
id: "load_shared_drives"
sidebar_position: 5
title: "load_shared_drives"
---

# ⚙️ load_shared_drives

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`folder_navigator.py`](./folder_navigator.py) | **Line:** 355
:::

Load and display available shared/team drives.

Switches view to Shared Drives, fetches accessible team drives
from Drive API, and displays as folder items. Clears navigation
history since shared drives are separate context.

## Returns

**Type**: `None`


## Algorithm

- 1. **Set View Context**:
    - a. Set dash.current_view = "shared_drives"
    - b. Indicates shared drive context

  - 2. **Reset Navigation**:
    - a. Set dash.folder_stack = [] (empty list)
    - b. Shared drives are root-level (no back navigation)

  - 3. **Clear UI**:
    - a. Call dash.folder_list.controls.clear()

  - 4. **Try Loading Drives**:
    - a. Enter try block for error handling
    - b. Call dash.drive.service.drives().list() with:
    - i. pageSize=100
    - ii. fields="drives(id, name)"
    - c. Call .execute() to perform request
    - d. Returns &#123;'drives': [...]&#125; or raises exception

  - 5. **Extract Drives**:
    - a. Get drives list: results.get("drives", [])
    - b. Each drive has 'id' and 'name'

  - 6. **Handle Results**:
    - a. If drives list empty:
    - i. Append message: "No shared drives found"
    - b. Else for each drive:
    - i. Create fake folder dict:
    - - id: drive["id"]
    - - name: drive["name"]
    - - mimeType: "application/vnd.google-apps.folder"
    - ii. Call file_manager.create_folder_item():
    - - fake_folder dict
    - - subfolder_count: 0 (not calculated)
    - - is_shared_drive: True (flag for behavior)
    - iii. Append to folder_list.controls

  - 7. **Handle Errors**:
    - a. Catch any Exception (API, network, parsing)
    - b. Append error message: "Error loading shared drives" (RED)

  - 8. **Update Display**:
    - a. Call dash.page.update()

## Interactions

- **DriveService.service.drives().list()**: Shared drives API
- **FileManager.create_folder_item()**: UI components
- **Dashboard.folder_list**: UI control

## Example

```python
# Load shared drives view
navigator.load_shared_drives()
# Dashboard shows:
# - "Team Marketing" (shared drive)
# - "Engineering Docs" (shared drive)
# - "Sales Resources" (shared drive)

# No shared drives
navigator.load_shared_drives()
# Shows: "No shared drives found"

# API error
navigator.load_shared_drives()
# Shows: "Error loading shared drives"
```

## See Also

- `load_your_folders()`: My Drive root view
- `show_folder_contents()`: Navigate into drive
- `Drives API <[https://developers.google.com/drive/api/v3/reference/drives>`_](https://developers.google.com/drive/api/v3/reference/drives>`_)

## Notes

- Shared drives separate from My Drive
- No subfolder count (performance)
- is_shared_drive flag affects navigation
- History stack cleared (separate context)
- Drive API separate endpoint from files
- Treats drives as special folders
- User must have access to see drives
