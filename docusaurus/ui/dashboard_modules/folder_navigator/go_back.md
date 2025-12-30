---
id: "go_back"
sidebar_position: 8
title: "go_back"
---

# ⚙️ go_back

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`folder_navigator.py`](./folder_navigator.py) | **Line:** 726
:::

Navigate to previous folder using history stack.

Pops previous context from history stack and restores that view.
Handles both folder navigation and root-level view restoration.
Mimics browser back button behavior.

## Returns

**Type**: `None`


## Algorithm

- 1. **Check History**:
    - a. If dash.folder_stack is empty:
    - i. No history to go back to
    - ii. Return early (no-op)

  - 2. **Pop Previous Context**:
    - a. Pop tuple from folder_stack: (fid, fname)
    - b. fid: previous folder ID
    - c. fname: previous folder name

  - 3. **Restore State**:
    - a. Set dash.current_folder_id = fid
    - b. Set dash.current_folder_name = fname
    - c. Dashboard now tracks previous folder

  - 4. **Route to Appropriate Loader**:
    - a. If fid == "root":
    - i. Returning to root-level view
    - ii. Check dash.current_view to determine which root:
    - - "your_folders": Call load_your_folders()
    - - "paste_links": Call paste_links_manager.load_paste_links_view()
    - - "shared_drives": Call load_shared_drives()
    - b. Else (specific folder):
    - i. Call show_folder_contents():
    - - folder_id: fid
    - - folder_name: fname
    - - push_to_stack: False (already popped)

## Interactions

- **Dashboard.folder_stack**: History stack (pop)
- **load_your_folders()**: Root view loader
- **load_shared_drives()**: Shared drives loader
- **show_folder_contents()**: Folder loader
- **PasteLinksManager.load_paste_links_view()**: Paste links view

## Example

```python
# Navigation sequence
navigator.load_your_folders()
# Stack: []

navigator.show_folder_contents('folder_1', 'Docs')
# Stack: [('root', 'My Drive')]

navigator.show_folder_contents('folder_2', 'Reports')
# Stack: [('root', 'My Drive'), ('folder_1', 'Docs')]

navigator.go_back()
# Returns to Docs folder
# Stack: [('root', 'My Drive')]

navigator.go_back()
# Returns to My Drive root
# Stack: []

navigator.go_back()
# No history, nothing happens
# Stack: []
```

## See Also

- `show_folder_contents()`: Sets up history
- `load_your_folders()`: Root view
- `load_shared_drives()`: Shared drives view

## Notes

- Mimics browser back button
- Stack stores (id, name) tuples
- Root ID always "root"
- Routes to correct root view based on context
- push_to_stack=False prevents re-adding to history
- Safe to call with empty stack (returns early)
- Maintains proper navigation context
