---
id: "save_saved_links"
sidebar_position: 5
title: "save_saved_links"
---

# ⚙️ save_saved_links

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`paste_links_manager.py`](./paste_links_manager.py) | **Line:** 374
:::

Save Drive links list to persistent JSON storage.

Writes provided links list to saved_links.json file, replacing
existing content. Creates file if doesn't exist.

## Parameters

- **`links`** (list[dict]): List of link dictionaries to save. Each dict should contain 'id', 'name', 'mimeType', 'url' keys. Can be empty list to clear saved links.

## Returns

**Type**: `None`


## Algorithm

- 1. **Try Saving File**:
    - a. Enter try block for error handling
    - b. Open SAVED_LINKS_FILE in write mode ('w')
    - c. Specify UTF-8 encoding
    - d. Use context manager for automatic closing

  - 2. **Write JSON**:
    - a. Create dict: &#123;"links": links&#125;
    - b. Call json.dump() with:
    - i. data: dict with links
    - ii. file handle: f
    - iii. indent: 2 (pretty print)
    - c. Writes formatted JSON to file

  - 3. **Handle Errors**:
    - a. Catch any Exception (write, permission, etc.)
    - b. Print error message with exception
    - c. File may not be updated

## Interactions

- **json.dump()**: JSON serialization
- **File I/O**: Opens and writes file

## Example

```python
# Save links list
links = [
    {
    'id': 'abc123',
    'name': 'Folder',
    'mimeType': 'application/vnd.google-apps.folder',
    'url': 'https://...'
    }
    ]
paste_manager.save_saved_links(links)
# File updated with links

# Clear saved links
paste_manager.save_saved_links([])
# File now contains: {"links": []}

# Permission error
paste_manager.save_saved_links(links)
# Prints: "Error saving saved links: ..."
```

## See Also

- `load_saved_links()`: Loads links from file
- `add_saved_link()`: Adds single link
- `delete_saved_link()`: Removes link

## Notes

- Overwrites existing file content
- indent=2 for readable JSON
- UTF-8 encoding for compatibility
- Creates file if doesn't exist
- Silent failure (prints error only)
- No return value
