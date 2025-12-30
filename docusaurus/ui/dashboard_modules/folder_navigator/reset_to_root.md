---
id: "reset_to_root"
sidebar_position: 9
title: "reset_to_root"
---

# ⚙️ reset_to_root

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`folder_navigator.py`](./folder_navigator.py) | **Line:** 825
:::

Reset navigation to My Drive root, clearing all history.

Clears navigation history stack and returns to My Drive root view.
Useful for "home" button or resetting navigation state.

## Returns

**Type**: `None`


## Algorithm

- 1. **Clear History**:
    - a. Set dash.folder_stack = [] (empty list)
    - b. Removes all back navigation

  - 2. **Reset State**:
    - a. Set dash.current_folder_id = "root"
    - b. Set dash.current_folder_name = "My Drive"

  - 3. **Load Root View**:
    - a. Call load_your_folders()
    - b. Displays My Drive root folders

## Interactions

- **Dashboard.folder_stack**: History clearing
- **load_your_folders()**: Root view loader

## Example

```python
# User deep in folder hierarchy
# Navigation: Root → Docs → 2024 → Reports
# Stack: [('root', 'My Drive'), ('folder_1', 'Docs'), ('folder_2', '2024')]

# User clicks "Home" button
navigator.reset_to_root()
# Returns to My Drive root
# Stack: []
# No back navigation available
```

## See Also

- `load_your_folders()`: Root view loader
- `go_back()`: Single-step back navigation

## Notes

- Clears entire history stack
- Always returns to My Drive (not shared drives)
- Useful for home button functionality
- Cannot go back after reset
- State fully reset to initial
