---
id: "get_folder_name_by_id"
sidebar_position: 6
title: "get_folder_name_by_id"
---

# ⚙️ get_folder_name_by_id

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`todo_view.py`](./todo_view.py) | **Line:** 724
:::

Resolve a Drive folder ID to its display name.

Attempts to find the folder name by checking saved links first,
then querying the Drive API if available. Provides fallback name
if folder cannot be resolved.

## Parameters

- **`folder_id`** (str): Google Drive folder ID to resolve. Example: '1abc...xyz' (33-character alphanumeric string).

## Returns

**Type**: `str`

                or "Linked Folder" if resolution fails.

## Algorithm

- 1. **Check Saved Links Cache**:
    - a. Iterate through self.saved_links list
    - b. For each link dictionary:
    - i. Check if link.get("id") == folder_id
    - ii. If match found:
    - - Return link.get("name", folder_id)
    - - Exits function immediately

  - 2. **Query Drive API** (if service available):
    - a. Check if self.drive_service is not None
    - b. If Drive service exists:
    - i. Try to call drive_service.get_file_info(folder_id)
    - ii. If info returned:
    - - Extract name: info.get('name', 'Linked Folder')
    - - Return folder name
    - iii. If exception occurs:
    - - Pass silently, continue to fallback

  - 3. **Return Fallback**:
    - a. If no match in saved links and no Drive service:
    - i. Return "Linked Folder" as default name

## Interactions

- **saved_links**: Searches in-memory link cache
- **DriveService.get_file_info()**: Queries Drive API for metadata
- **Drive API**: Retrieves folder/file information

## Example

```python
# Folder in saved links
name = todo_view.get_folder_name_by_id('1abc...xyz')
print(name)
# Assignments Folder

# Folder not in links, query Drive
name = todo_view.get_folder_name_by_id('2def...uvw')
print(name)
# Project Resources

# Folder not found anywhere
name = todo_view.get_folder_name_by_id('invalid_id')
print(name)
# Linked Folder
```

## See Also

- `load_saved_links()`: Loads saved links cache
- `DriveService`: Drive API wrapper

## Notes

- Two-tier lookup: saved links first, then Drive API
- Saved links check is fast (in-memory)
- Drive API call is slower (network request)
- Gracefully handles missing Drive service
- Gracefully handles API errors
- Returns generic name if resolution fails
- Used for displaying folder names in UI
