---
id: "find_file"
sidebar_position: 19
title: "find_file"
---

# ⚙️ find_file

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`drive_service.py`](./drive_service.py) | **Line:** 1732
:::

Find file by exact name in specific folder.

Searches for file with exact name match in given folder.
Case-sensitive search.

## Parameters

- **`name`** (str): Exact filename to find. Must match exactly including case and extension.
- **`parent_id`** (str): Folder ID to search within.

## Returns

**Type**: `dict or None`

                - id (str): File ID
                - name (str): File name
                - mimeType (str): MIME type
                - modifiedTime (str): Modification timestamp
                Returns None if not found.

## Algorithm

- **Phase 1: Build Query**
  - 1. Format: "name = '&#123;name&#125;' and '&#123;parent_id&#125;' in parents and trashed=false"
  - 2. Exact name match (case-sensitive)
  - 3. Must be in specified parent
  - 4. Must not be trashed


- **Phase 2: Execute Query**
  - 1. Call service.files().list() with:
  - 2. q: query string
    - a. pageSize: 1 (only need first match)
    - b. fields: minimal set
  - 3. Execute request
  - 4. Returns results dictionary


- **Phase 3: Extract Files**
  - 1. Get files list: results.get('files', [])


- **Phase 4: Return Result**
  - 1. If files list not empty:
  - 2. Return files[0] (first match)
  - 3. If files list empty:
  - 4. Return None (not found)

## Interactions

- **service.files().list()**: Drive query API

## Example

```python
# Find specific file
file = drive.find_file('document.pdf', parent_id='folder_id')
if file:
    print(f"Found: {file['id']}")
    else:
    print("Not found")

# Check existence before upload
existing = drive.find_file('report.txt', 'root')
if existing:
    drive.update_file(existing['id'], 'report.txt')
    else:
    drive.upload_file('report.txt')
```

## See Also

- `search_files()`: Partial name search
- `list_files()`: List all files in folder

## Notes

- Exact name match (case-sensitive)
- Returns first match only
- Search within single folder only
- Excludes trashed files
- Returns None if not found
- pageSize=1 for efficiency
