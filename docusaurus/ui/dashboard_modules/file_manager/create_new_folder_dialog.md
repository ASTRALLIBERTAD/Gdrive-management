---
id: "create_new_folder_dialog"
sidebar_position: 14
title: "create_new_folder_dialog"
---

# ⚙️ create_new_folder_dialog

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`file_manager.py`](./file_manager.py) | **Line:** 1349
:::

Display modal dialog for creating new folder in current directory.

Shows input dialog for folder name. On creation, calls Drive API,
performs optimistic UI update (adds folder to list immediately),
and invalidates cache for consistency.

## Returns

**Type**: `None`


## Algorithm

- 1. **Create Input Controls**:
    - a. Create name_field (ft.TextField):
    - i. label: "Folder name"
    - ii. autofocus: True
    - b. Create loading_text (ft.Text):
    - i. Initial value: "" (empty)
    - ii. Shows status messages

  - 2. **Define Create Handler**:
    - a. Validate input:
    - i. Get folder_name: name_field.value.strip()
    - ii. If empty, return (no-op)
    - b. Show loading:
    - i. Set loading_text.value = "Creating folder..."
    - ii. Call dash.page.update()
    - c. Call API:
    - i. dash.drive.create_folder(folder_name, parent_id)
    - ii. parent_id = dash.current_folder_id
    - iii. Returns folder metadata dict or None
    - d. Handle success:
    - i. If folder is not None:
    - - Remove dialog: dash.page.overlay.pop()
    - - Create UI item:
    - - Call create_folder_item() with:
    - - folder: &#123;'id', 'name', 'mimeType'&#125;
    - - subfolder_count: 0 (new folder empty)
    - - Optimistic update:
    - - insert_position = 1 (after back button)
    - - If space available:
    - - Insert at position 1
    - - Else:
    - - Append to end
    - - Invalidate cache:
    - - dash.drive._invalidate_cache(current_folder_id)
    - - Update UI:
    - - dash.page.update()
    - e. Handle failure:
    - i. If folder is None:
    - - Set loading_text.value = "Failed to create folder."
    - - Call dash.page.update()
    - - Dialog remains open

  - 3. **Build Dialog UI**:
    - a. Create dialog_container:
    - i. Title: "Create New Folder"
    - ii. Input field: name_field
    - iii. Status text: loading_text
    - iv. Action Row:
    - - Cancel: pops overlay, updates
    - - Create: calls create handler
    - v. Dimensions: 350x200px
    - vi. White background, rounded

  - 4. **Show Dialog**:
    - a. Append to dash.page.overlay
    - b. Call dash.page.update()

## Interactions

- **DriveService.create_folder()**: API folder creation
- **create_folder_item()**: UI component creation
- **DriveService._invalidate_cache()**: Cache management
- **Dashboard.current_folder_id**: Parent folder tracking
- **ft.TextField**: Input control

## Example

```python
# User clicks "New Folder" button
file_manager.create_new_folder_dialog()
# Dialog appears with input field focused

# User enters "My New Folder" and clicks Create
# → Shows: "Creating folder..."
# → API: create_folder("My New Folder", current_folder_id)
# → Returns: {'id': 'new_123', 'name': 'My New Folder'}
# → Creates folder item UI component
# → Inserts at position 1 in list (below back button)
# → Cache invalidated for current folder
# → Dialog closes
# → New folder visible in list immediately

# Empty name (validation failure)
# User clicks Create with empty field
# → Nothing happens (early return)

# API failure
# API returns None (error occurred)
# → Shows: "Failed to create folder."
# → Dialog stays open
# → User can retry or cancel
```

## See Also

- `create_folder_item()`: UI component creation
- `create_folder()`: API method
- `current_folder_id()`: State tracking

## Notes

- Optimistic UI update (shows before full refresh)
- Validates non-empty name
- Loading message during API call
- Inserts at position 1 (after back button)
- Cache invalidation ensures consistency
- Dialog stays open on failure (retry possible)
- New folders start with 0 subfolders
- Modal blocks interaction during creation
