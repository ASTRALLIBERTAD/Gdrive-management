---
id: "get_folder_tree"
sidebar_position: 23
title: "get_folder_tree"
---

# ⚙️ get_folder_tree

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`drive_service.py`](./drive_service.py) | **Line:** 2117
:::

Recursively retrieve nested folder structure.

Builds hierarchical folder tree up to specified depth.
Useful for folder navigation UI components.

## Parameters

- **`folder_id`** (str, optional): Root folder ID to start from. Use 'root' for Drive root. Defaults to 'root'.
- **`max_depth`** (int, optional): Maximum recursion depth. 0 returns no children, 1 returns immediate children, 2 returns grandchildren, etc. Defaults to 2.
- **`current_depth`** (int, optional): Current recursion depth. Internal parameter for recursion tracking. Should not be set by caller. Defaults to 0.

## Returns

**Type**: `list or None`


## Algorithm

- **Phase 1: Check Depth Limit**
  - 1. If current_depth &gt;= max_depth:
  - 2. Return None (depth limit reached)


- **Phase 2: Build Query**
  - 1. Format: "'&#123;folder_id&#125;' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
  - 2. Filters: in folder, is folder type, not trashed


- **Phase 3: Execute Query**
  - 1. Call _execute_file_list_query() with:
  - 2. query: folder filter
    - a. page_size: 100
    - b. fields: 'files(id, name)' (minimal)
    - c. order_by: 'name' (alphabetical)
  - 3. Returns result or None


- **Phase 4: Extract Folders**
  - 1. If result is dict:
  - 2. Get folders: result.get('files', [])
  - 3. If result is None:
  - 4. folders = [] (empty list)


- **Phase 5: Recurse for Children**
  - 1. For each folder in folders:
  - 2. Recursively call get_folder_tree() with:
    - - folder_id: folder['id']
    - - max_depth: max_depth (unchanged)
    - - current_depth: current_depth + 1
    - a. Store result in folder['children']
    - b. Will be list or None


- **Phase 6: Return Tree**
  - 1. Return folders list with populated children

## Interactions

- **_execute_file_list_query()**: Query folders
- **Recursive self-call**: Builds tree structure

## Example

```python
# Get 2-level folder tree
tree = drive.get_folder_tree('root', max_depth=2)
for folder in tree:
    print(f"📁 {folder['name']}")
    if folder['children']:
    for child in folder['children']:
    print(f"  📁 {child['name']}")

# Single level (immediate children only)
tree = drive.get_folder_tree('folder_id', max_depth=1)

# Deep tree
tree = drive.get_folder_tree('root', max_depth=5)
# Warning: May be slow for large structures
```

## See Also

- `list_files()`: List files and folders
- `create_folder()`: Create folders

## Notes

- Recursive algorithm
- max_depth limits recursion
- Only includes folders (not files)
- Excludes trashed folders
- children=None at max depth
- children=[] if no subfolders
- Alphabetically sorted by name
- Can be slow for deep/large trees
- current_depth for internal use only
