---
id: "move_file"
sidebar_position: 20
title: "move_file"
---

# ⚙️ move_file

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`drive_service.py`](./drive_service.py) | **Line:** 1818
:::

Move file or folder to different parent folder.

Removes file from current parent(s) and adds to new parent.
Invalidates cache for both old and new parent folders.

## Parameters

- **`file_id`** (str): ID of file or folder to move.
- **`new_parent_id`** (str): Destination folder ID.

## Returns

**Type**: `dict or None`

                - id (str): File ID (unchanged)
                - parents (list): New parent IDs (only new_parent_id)
                Returns None if move fails.

## Algorithm

- **Phase 1: Define Request Function**
  - 1. Create make_request() closure
  - 2. Get current parents:
  - 3. Call service.files().get(fileId, fields='parents')
    - a. Extract parents list
    - b. Join with commas: ",".join(parents)
  - 4. Update file:
  - 5. Call service.files().update()
    - a. addParents: new_parent_id
    - b. removeParents: previous_parents (comma-separated)
    - c. fields: 'id, parents'
  - 6. Execute and return


- **Phase 2: Execute with Retry**
  - 1. Call _retry_request(make_request, operation_name)
  - 2. Returns updated_file or None


- **Phase 3: Invalidate Caches (if successful)**
  - 1. If updated_file not None:
  - 2. Get fresh parent list
    - a. Invalidate old parents:
    - - Get file info to find old parents
    - - Invalidate each old parent cache
    - b. Invalidate new parent: _invalidate_cache(new_parent_id)


- **Phase 4: Return Result**
  - 1. Return updated_file (success) or None (failure)

## Interactions

- **service.files().get()**: Get current parents
- **service.files().update()**: Move operation
- **_retry_request()**: Retry wrapper
- **_invalidate_cache()**: Cache management

## Example

```python
# Move file to new folder
result = drive.move_file('file_id', 'new_folder_id')
if result:
    print(f"Moved to: {result['parents']}")

# Move to root
result = drive.move_file('file_id', 'root')

# Handle failure
result = drive.move_file('invalid_id', 'folder_id')
if not result:
    print("Move failed")
```

## See Also

- `rename_file()`: Rename without moving
- `create_folder()`: Create destination folder

## Notes

- Removes from all current parents
- Adds to single new parent
- File can have multiple parents (uncommon)
- Invalidates both old and new parent caches
- Returns None on failure
- Parent change tracked in parents field
