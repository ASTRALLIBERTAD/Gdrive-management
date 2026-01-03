---
id: "delete_file"
sidebar_position: 22
title: "delete_file"
---

# ⚙️ delete_file

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`drive_service.py`](./drive_service.py) | **Line:** 2015
:::

Permanently delete file or folder from Drive.

Deletes file and invalidates all related caches. Cannot be undone.

## Parameters

- **`file_id`** (str): ID of file or folder to delete.

## Returns

**Type**: `bool`


## Algorithm

- **Phase 1: Get File Info First**
  - 1. Call get_file_info(file_id, use_cache=False)
  - 2. Need parent info for cache invalidation
  - 3. Store in file_info


- **Phase 2: Define Request Function**
  - 1. Create make_request() closure
  - 2. Call service.files().delete(fileId=file_id)
  - 3. Execute request (returns None on success)
  - 4. Return True to indicate success


- **Phase 3: Execute with Retry**
  - 1. Call _retry_request(make_request, operation_name)
  - 2. Returns True or None
  - 3. Store in success variable


- **Phase 4: Invalidate Caches (if successful)**
  - 1. If success is True:
  - 2. If file_info exists and has 'parents':
    - - For each parent in file_info['parents']:
    - - Call _invalidate_cache(parent)
    - a. Call _invalidate_cache(file_id)
    - b. Return True


- **Phase 5: Return Failure**
  - 1. If success is None or False:
  - 2. Return False

## Interactions

- **get_file_info()**: Get parent info
- **service.files().delete()**: Drive delete API
- **_retry_request()**: Retry wrapper
- **_invalidate_cache()**: Cache management

## Example

```python
# Delete file
success = drive.delete_file('file_id')
if success:
    print("Deleted successfully")
    else:
    print("Deletion failed")

# Delete folder (recursive)
success = drive.delete_file('folder_id')
# Deletes folder and all contents

# Confirm before delete
file = drive.get_file_info('file_id')
confirm = input(f"Delete {file['name']}? (y/n): ")
if confirm.lower() == 'y':
    drive.delete_file('file_id')
```

## See Also

- `get_file_info()`: Get file info before delete
- `list_files()`: Verify deletion

## Notes

- Permanent deletion (not trash)
- Folder deletion is recursive
- Invalidates parent caches
- Returns bool (not dict)
- File info fetched for cache invalidation
- Cannot be undone
- Deletes all folder contents if folder
