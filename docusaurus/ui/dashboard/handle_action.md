---
id: "handle_action"
sidebar_position: 11
title: "handle_action"
---

# ⚙️ handle_action

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`dashboard.py`](./dashboard.py) | **Line:** 938
:::

Handle sidebar menu action selection.

Routes user-selected actions from the dropdown menu to appropriate
handler methods. Supports file operations like creating folders
and uploading files through the file_manager module.

## Parameters

- **`selected_item`** (str): Selected menu option text. Expected values: "Create Folder", "Upload File". Must match exact button text from ButtonWithMenu component. Case-sensitive.

## Returns

**Type**: `None`


## Algorithm

- 1. **Action Routing**:
    - a. Check if selected_item == "Create Folder"
    - i. If True, call file_manager.create_new_folder_dialog()
    - ii. Opens dialog for entering new folder name
    - iii. Dialog handles folder creation on confirm
    - b. Check elif selected_item == "Upload File"
    - i. If True, call file_manager.select_file_to_upload()
    - ii. Opens system file picker dialog
    - iii. Handles file selection and upload process

  - 2. **Update UI**:
    - a. Call self.page.update()
    - b. Ensures any dialog or state changes are rendered
    - c. Maintains UI responsiveness

## Interactions

- **FileManager**: Delegates to create_new_folder_dialog() or select_file_to_upload()
- **ButtonWithMenu**: Provides selected_item from dropdown
- **ft.Page**: Updates to render dialogs or changes

## Example

```python
# User clicks "+ NEW" and selects "Create Folder"
dashboard.handle_action("Create Folder")
# Opens folder creation dialog
# User enters "My Project" and confirms
# New folder created in current directory

# User clicks "+ NEW" and selects "Upload File"
dashboard.handle_action("Upload File")
# Opens system file picker
# User selects file and confirms
# File uploads to current folder
```

## See Also

- `FileManager`: File operations
- `ButtonWithMenu`: Dropdown menu
- `get_view()`: Creates "+ NEW" button with menu

## Notes

- Only handles file operations currently
- Extensible for additional menu actions
- selected_item must match exact menu option text
- file_manager handles all dialog creation and logic
- Page update called regardless of action taken
- Invalid selected_item values are ignored (no action)
