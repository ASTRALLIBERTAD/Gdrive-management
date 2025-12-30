---
id: "extract_drive_id"
sidebar_position: 5
title: "extract_drive_id"
---

# ⚙️ extract_drive_id

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`common.py`](./common.py) | **Line:** 362
:::

Extract Google Drive file or folder ID from various URL formats.

Parses Google Drive URLs using regex patterns to extract the file or
folder ID. Supports multiple Drive URL formats including file links,
folder links, and query parameter formats. Returns raw input if it
appears to already be an ID.

## Purpose

- Parse Drive URLs to extract file/folder IDs
        - Support multiple URL formats (folders, files, query params)
        - Handle raw ID input (pass-through)
        - Enable ID-based Drive API operations

## Parameters

- **`url`** (str): Google Drive URL or ID to parse. Supported formats: - Folder: "`https://drive.google.com/drive/folders/&#123;id&#125;"` - File: "`https://drive.google.com/file/d/&#123;id&#125;/view"` - Query param: "...?id=&#123;id&#125;" - Raw ID: alphanumeric string without slashes

## Returns

**Type**: `str | None`

            Returns input string if it appears to be raw ID (length > 20,
            no slashes). Drive IDs typically 33 characters alphanumeric.

## Algorithm

- 1. **Import Regex Module**:
- a. Import re for regex pattern matching

- 2. **Define URL Patterns**:
- a. Create patterns list with regex strings:
  - i. r"/folders/([a-zA-Z0-9_-]+)" - folder URLs
  - ii. r"/file/d/([a-zA-Z0-9_-]+)" - file URLs
  - iii. r"[?&]id=([a-zA-Z0-9_-]+)" - query parameter URLs
- b. Patterns capture ID in group 1

- 3. **Try Pattern Matching**:
- a. For each pattern in patterns list:
  - i. Call re.search(pattern, url)
  - ii. If match found:
    - - Extract ID: match.group(1)
    - - Return ID immediately

- 4. **Check for Raw ID**:
- a. If no pattern matched:
  - i. Check if len(url) > 20 (IDs typically ~33 chars)
  - ii. Check if "/" not in url (IDs have no slashes)
  - iii. If both conditions true:
    - - Assume url is already an ID
    - - Return url as-is

- 5. **Return None**:
- a. If no matches and not raw ID:
  - i. Return None (invalid URL/ID)

## Interactions

- **re.search()**: Regex pattern matching
- **re.Match.group()**: Extract captured group

## Example

```python
# Folder URL
url = "https://drive.google.com/drive/folders/1abc...xyz"
extract_drive_id(url)
# '1abc...xyz'

# File URL
url = "https://drive.google.com/file/d/1def...uvw/view"
extract_drive_id(url)
# '1def...uvw'

# Query parameter URL
url = "https://drive.google.com/open?id=1ghi...rst"
extract_drive_id(url)
# '1ghi...rst'

# Raw ID (pass-through)
id_str = "1jklmnopqrstuvwxyz123456789012"
extract_drive_id(id_str)
# '1jklmnopqrstuvwxyz123456789012'

# Invalid URL
extract_drive_id("https://example.com")
# None

# Short string (not ID)
extract_drive_id("short")
# None
```

## See Also

- `open_drive_file()`: Opens file using extracted ID
- `open_drive_folder()`: Opens folder using extracted ID
- `DriveService`: Uses IDs for API calls

## Notes

- Supports folder, file, and query parameter URL formats
- Drive IDs are alphanumeric with hyphens/underscores
- Typical ID length is 33 characters
- Raw ID detection uses length > 20 and no slashes
- Returns None for invalid/unrecognized formats
- Case-sensitive pattern matching (Drive IDs case-sensitive)
- Thread-safe (no state modification)
