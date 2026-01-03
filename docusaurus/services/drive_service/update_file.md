---
id: "update_file"
sidebar_position: 17
title: "update_file"
---

# ⚙️ update_file

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`drive_service.py`](./drive_service.py) | **Line:** 1500
:::

Update existing file's content and optionally rename.

Replaces file content with new data from local file. Can also
rename file in single operation.

## Parameters

- **`file_id`** (str): ID of file to update in Drive.
- **`file_path`** (str): Path to local file with new content.
- **`new_name`** (str, optional): New name for file in Drive. If None, name unchanged. Defaults to None.

## Returns

**Type**: `dict or None`

                - id (str): File ID (unchanged)
                - name (str): File name (new if renamed)
                - mimeType (str): MIME type
                - modifiedTime (str): New modification timestamp
                Returns None on update failure.

## Algorithm

- **Phase 1: Try Update Process**
  - 1. Enter try block for error handling


- **Phase 2: Build Metadata**
  - 1. Create empty file_metadata dictionary
  - 2. If new_name provided:
  - 3. Add to metadata: file_metadata['name'] = new_name


- **Phase 3: Create Media Upload**
  - 1. Instantiate MediaFileUpload(file_path, resumable=True)
  - 2. Loads new file content


- **Phase 4: Execute Update**
  - 1. Call service.files().update() with:
  - 2. fileId: file_id
    - a. body: file_metadata (name if provided)
    - b. media_body: media object
    - c. fields: 'id, name, mimeType, modifiedTime'
  - 3. Execute request
  - 4. Returns updated file dict


- **Phase 5: Invalidate Cache**
  - 1. Call _invalidate_cache(file_id)
  - 2. Clears cached file info


- **Phase 6: Return Result**
  - 1. Return updated_file dictionary


- **Phase 7: Handle Errors**
  - 1. Catch any Exception
  - 2. Print error message
  - 3. Return None

## Interactions

- **MediaFileUpload**: Handles file upload
- **service.files().update()**: Drive update API
- **_invalidate_cache()**: Cache management

## Example

```python
# Update content only
result = drive.update_file('file_id', 'new_content.txt')
print(f"Updated: {result['modifiedTime']}")

# Update and rename
result = drive.update_file(
    'file_id',
    'new_content.pdf',
    new_name='Report Final.pdf'
    )

# Handle failure
result = drive.update_file('invalid_id', 'file.txt')
if not result:
    print("Update failed")
```

## See Also

- `upload_file()`: Upload new file
- `rename_file()`: Rename without updating content

## Notes

- Replaces entire file content
- Optional rename in same operation
- Resumable upload for reliability
- Invalidates file cache
- modifiedTime updated automatically
- Returns None on failure
