---
id: "load_saved_links"
sidebar_position: 5
title: "load_saved_links"
---

# ⚙️ load_saved_links

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`todo_view.py`](./todo_view.py) | **Line:** 649
:::

Load legacy saved link shortcuts from JSON file.

Reads the saved_links.json file containing Drive folder shortcuts
and returns the links list. This is a legacy feature maintained
for backward compatibility.

## Returns

**Type**: `list`

                - id (str): Drive folder/file ID
                - name (str): Display name for link
                - url (str): Full Drive URL
                Returns empty list if file doesn't exist or can't be parsed.

## Algorithm

- 1. **Check File Existence**:
    - a. Check if SAVED_LINKS_FILE ("saved_links.json") exists
    - b. Use os.path.exists() for file check

  - 2. **Load File** (if exists):
    - a. Try to open file with UTF-8 encoding
    - b. Parse JSON content with json.load()
    - c. Extract "links" key from data dictionary
    - d. Return links list

  - 3. **Handle Errors**:
    - a. If any exception occurs (IOError, JSONDecodeError):
    - i. Catch exception silently
    - ii. Continue to return empty list

  - 4. **Return Default**:
    - a. If file doesn't exist or error occurs:
    - i. Return empty list []

## Interactions

- **os.path.exists()**: Checks file existence
- **json.load()**: Parses JSON content
- **File I/O**: Reads from saved_links.json

## Example

```python
# File exists with data
links = todo_view.load_saved_links()
print(links)
# [
# {'id': '1abc...', 'name': 'Assignments', 'url': 'https://...'},
# {'id': '2def...', 'name': 'Resources', 'url': 'https://...'}
# ]

# File doesn't exist
links = todo_view.load_saved_links()
print(links)
# []
```

## See Also

- `__init__()`: Calls this during initialization
- `get_folder_name_by_id()`: Uses saved links for name resolution

## Notes

- Legacy feature for Drive folder shortcuts
- File stored in current working directory
- Returns empty list on any error (graceful failure)
- JSON structure: &#123;"links": [&#123;"id": ..., "name": ..., "url": ...&#125;]&#125;
- Not actively used in new implementations
- Maintained for backward compatibility
