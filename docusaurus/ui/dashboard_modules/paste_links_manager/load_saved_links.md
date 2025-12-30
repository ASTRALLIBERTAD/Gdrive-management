---
id: "load_saved_links"
sidebar_position: 4
title: "load_saved_links"
---

# ⚙️ load_saved_links

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`paste_links_manager.py`](./paste_links_manager.py) | **Line:** 277
:::

Load saved Drive links from persistent JSON storage.

Reads saved_links.json file and returns list of previously saved
Drive links. Creates empty list if file doesn't exist or on errors.

## Returns

**Type**: `list[dict]`

                - 'id' (str): Drive file or folder ID
                - 'name' (str): Display name for link
                - 'mimeType' (str): MIME type (folder or file type)
                - 'url' (str): Original pasted URL
                Returns empty list [] if file missing or error occurs.

## Algorithm

- 1. **Check File Existence**:
    - a. Check if SAVED_LINKS_FILE exists
    - b. If not exists, return empty list []

  - 2. **Try Loading File**:
    - a. Enter try block for error handling
    - b. Open SAVED_LINKS_FILE in read mode
    - c. Specify UTF-8 encoding
    - d. Parse JSON content with json.load()
    - e. Store in data variable

  - 3. **Extract Links**:
    - a. Get 'links' key from data dict
    - b. Use .get("links", []) for safe access
    - c. Return links list

  - 4. **Handle Errors**:
    - a. Catch any Exception (parse, read, etc.)
    - b. Print error message with exception
    - c. Return empty list [] (graceful failure)

  - 5. **Default Return**:
    - a. If file doesn't exist
    - b. Return empty list []

## Interactions

- **os.path.exists()**: File existence check
- **json.load()**: JSON parsing
- **File I/O**: Opens and reads file

## Example

```python
# Load existing links
links = paste_manager.load_saved_links()
print(links)
# [
# {
# 'id': 'abc123',
# 'name': 'Project Folder',
# 'mimeType': 'application/vnd.google-apps.folder',
# 'url': 'https://drive.google.com/drive/folders/abc123'
# },
# {
# 'id': 'xyz789',
# 'name': 'Document.pdf',
# 'mimeType': 'application/pdf',
# 'url': 'https://drive.google.com/file/d/xyz789/view'
# }
# ]

# No saved links (file doesn't exist)
links = paste_manager.load_saved_links()
print(links)
# []

# Corrupted JSON file
links = paste_manager.load_saved_links()
# Prints: "Error loading saved links: ..."
print(links)
# []
```

## See Also

- `save_saved_links()`: Saves links to file
- `add_saved_link()`: Adds new link
- `build_saved_links_ui()`: Displays links

## Notes

- File: saved_links.json (module constant)
- UTF-8 encoding for international characters
- Graceful failure returns empty list
- No file created by this method
- JSON structure: &#123;"links": [...]&#125;
