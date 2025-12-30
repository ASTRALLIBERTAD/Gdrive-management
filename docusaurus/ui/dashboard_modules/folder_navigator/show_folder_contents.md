---
id: "show_folder_contents"
sidebar_position: 6
title: "show_folder_contents"
---

# ⚙️ show_folder_contents

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`folder_navigator.py`](./folder_navigator.py) | **Line:** 463
:::

Display contents of specified folder with back navigation support.

Main navigation method that loads and displays folder contents,
manages history stack for back button, shows loading states, and
handles errors. Updates Dashboard state and UI with folder items.

## Parameters

- **`folder_id`** (str): Drive ID of folder to display. Use "root" for My Drive root. Required parameter for content fetching.
- **`folder_name`** (str, optional): Display name for folder header and breadcrumb. If None, uses folder_id as fallback. Defaults to None.
- **`is_shared_drive`** (bool, optional): Whether folder is within shared drive context. May affect permissions and behavior. Defaults to False.
- **`push_to_stack`** (bool, optional): Whether to save current context to history stack before navigating. Set False for refresh or back navigation to prevent duplicate entries. Defaults to True.

## Returns

**Type**: `None`


## Algorithm

- 1. **Determine Display Name**:
    - a. If folder_name provided: use folder_name
    - b. Else: use folder_id as fallback
    - c. Store in display_name

  - 2. **Manage Navigation History**:
    - a. If push_to_stack is True:
    - i. Check if current_folder_id != folder_id (not same folder)
    - ii. If different:
    - - Create tuple: (current_folder_id, current_folder_name)
    - - Append to dash.folder_stack
    - - Enables back button

  - 3. **Update Context State**:
    - a. Set dash.current_folder_id = folder_id
    - b. Set dash.current_folder_name = display_name
    - c. Dashboard now tracks new folder

  - 4. **Clear UI**:
    - a. Call dash.folder_list.controls.clear()
    - b. Removes all previous items

  - 5. **Build Navigation Controls**:
    - a. Initialize back_controls = [] (empty list)
    - b. If dash.folder_stack has items (history exists):
    - i. Create IconButton:
    - - icon: ARROW_BACK
    - - on_click: lambda calls go_back()
    - ii. Append to back_controls

  - 6. **Create Header Row**:
    - a. Create ft.Row with:
    - i. *back_controls (unpacked, may be empty)
    - ii. Text: display_name (size 18, bold)
    - iii. ElevatedButton:
    - - text: "Refresh"
    - - icon: REFRESH
    - - on_click: lambda calls refresh_folder_contents()
    - iv. alignment: SPACE_BETWEEN
    - b. Append to folder_list.controls

  - 7. **Show Loading State**:
    - a. Create loading_indicator (ft.Row):
    - i. ProgressRing (20x20)
    - ii. Text: "Loading folder contents..." (size 14)
    - b. Append to folder_list.controls
    - c. Call dash.page.update() to show immediately

  - 8. **Try Loading Contents**:
    - a. Enter try block
    - b. Call dash.drive.list_files():
    - i. folder_id: target folder
    - ii. page_size: 200 (more items)
    - iii. use_cache: False (fresh data)
    - c. Returns result dict or None

  - 9. **Remove Loading Indicator**:
    - a. Call folder_list.controls.remove(loading_indicator)
    - b. Clears loading state

  - 10. **Handle API Result**:
    - a. If result is None:
    - i. Network error occurred
    - ii. Append message: "Network error" (ORANGE)
    - b. If result is dict:
    - i. Extract files: result.get("files", [])
    - ii. If files empty:
    - - Append message: "Folder is empty"
    - iii. Else for each file:
    - - Call file_manager.create_file_item(file)
    - - Append to folder_list.controls

  - 11. **Handle Errors**:
    - a. Catch any Exception
    - b. Append error message: "Error loading folder contents" (RED)

  - 12. **Update Display**:
    - a. Call dash.page.update()
    - b. Renders final state

## Interactions

- **DriveService.list_files()**: Fetches folder contents
- **FileManager.create_file_item()**: Creates UI items
- **Dashboard.folder_stack**: History management
- **ft.IconButton**: Back button
- **ft.ProgressRing**: Loading indicator

## Example

```python
# Navigate into folder
navigator.show_folder_contents(
    folder_id='folder_abc123',
    folder_name='Documents'
    )
# Shows:
# [<-] Documents [Refresh]
# - report.pdf
# - meeting_notes.txt
# - subfolder/

# Refresh current folder (no stack push)
navigator.show_folder_contents(
    folder_id='folder_abc123',
    folder_name='Documents',
    push_to_stack=False
    )
# Reloads without adding to history

# Navigate with fallback name
navigator.show_folder_contents(
    folder_id='folder_xyz789'
    )
# Header shows: folder_xyz789 (ID as name)

# Shared drive folder
navigator.show_folder_contents(
    folder_id='shared_folder_123',
    folder_name='Team Resources',
    is_shared_drive=True
    )
```

## See Also

- `go_back()`: Back navigation
- `refresh_folder_contents()`: Refresh wrapper
- `list_files()`: API method

## Notes

- Loading indicator shows immediately (better UX)
- Back button only if history exists
- Refresh button always present
- push_to_stack=False prevents duplicate history
- use_cache=False ensures fresh data
- Page size 200 (larger than root load)
- Error states handled gracefully
- Empty folders show friendly message
- Both files and folders displayed
