---
id: "show_folder_menu"
sidebar_position: 10
title: "show_folder_menu"
---

# ⚙️ show_folder_menu

![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`file_manager.py`](./file_manager.py) | **Line:** 873
:::

Open folder navigation (legacy alias for open_folder).

Alternate entry point for folder navigation. Delegates to open_folder
for actual implementation. Maintained for backward compatibility.

## Parameters

- **`folder`** (dict): Folder metadata with 'id' and optional 'name'.
- **`is_shared_drive`** (bool, optional): Shared drive flag. Defaults to False.

## Returns

**Type**: `None`


## See Also

- `open_folder()`: Actual implementation

## Notes

- Legacy method (may be deprecated)
- Direct alias to open_folder
- Same behavior and arguments
