---
id: "add_saved_link"
sidebar_position: 6
title: "add_saved_link"
---

# ⚙️ add_saved_link

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`paste_links_manager.py`](./paste_links_manager.py) | **Line:** 452
:::

Add new Drive link to saved history if not duplicate.

Appends validated Drive link to saved links list, checking for
duplicates by file ID. Saves updated list to JSON storage.

## Parameters

- **`file_id`** (str): Drive file or folder ID. Used for duplicate detection.
- **`info`** (dict): File metadata from Drive API containing: - 'name' (str): Display name - 'mimeType' (str): MIME type Additional keys may be present but not used.
- **`original_url`** (str): Original pasted URL for reference and re-access.

## Returns

**Type**: `bool`


## Algorithm

- 1. **Load Current Links**:
    - a. Call self.load_saved_links()
    - b. Returns list of existing links

  - 2. **Check for Duplicate**:
    - a. Use any() with generator expression
    - b. Check if any link has matching ID
    - c. Expression: any(l.get("id") == file_id for l in links)
    - d. If duplicate found:
    - i. Return False (not added)

  - 3. **Append New Link**:
    - a. Create link dict:
    - i. id: file_id
    - ii. name: info.get("name", file_id) (fallback to ID)
    - iii. mimeType: info.get("mimeType", "") (empty if missing)
    - iv. url: original_url
    - b. Append dict to links list

  - 4. **Save Updated List**:
    - a. Call self.save_saved_links(links)
    - b. Persists to JSON file

  - 5. **Return Success**:
    - a. Return True (link added)

## Interactions

- **load_saved_links()**: Retrieves current list
- **save_saved_links()**: Persists updated list

## Example

```python
# Add new link
info = {
    'name': 'Project Folder',
    'mimeType': 'application/vnd.google-apps.folder'
    }
added = paste_manager.add_saved_link(
    'abc123',
    info,
    'https://drive.google.com/drive/folders/abc123'
    )
print(added)
# True

# Try adding same link again (duplicate)
added = paste_manager.add_saved_link(
    'abc123',
    info,
    'https://drive.google.com/drive/folders/abc123'
    )
print(added)
# False

# Add file link
file_info = {'name': 'Doc.pdf', 'mimeType': 'application/pdf'}
added = paste_manager.add_saved_link('xyz789', file_info, 'https://...')
print(added)
# True
```

## See Also

- `load_saved_links()`: Retrieves existing links
- `save_saved_links()`: Persists to storage
- `handle_paste_link()`: Calls this after validation

## Notes

- Duplicate detection by file ID only
- Same ID with different URL still considered duplicate
- Name fallback to ID if missing
- MIME type empty string if missing
- Original URL preserved for reference
- Returns bool for feedback to caller
