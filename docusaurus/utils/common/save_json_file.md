---
id: "save_json_file"
sidebar_position: 3
title: "save_json_file"
---

# ⚙️ save_json_file

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`common.py`](./common.py) | **Line:** 135
:::

Save Python data structure to a JSON file with formatting.

Serializes Python data to JSON format and writes it to the specified
file. Provides human-readable formatting with indentation, handles
special types like datetime, and ensures proper Unicode encoding.

## Purpose

- Serialize Python objects to JSON format
        - Write JSON data to filesystem
        - Format JSON with indentation for readability
        - Handle special types (datetime, etc.) via str() conversion
        - Preserve Unicode characters (no ASCII escaping)

## Parameters

- **`filepath`** (str | Path): Destination path for JSON file. Can be string path or pathlib.Path object. Automatically converts strings to Path for consistent handling. File created if doesn't exist; overwritten if exists.
- **`data`** (any): Python object to serialize. Must be JSON-serializable. Supported types: dict, list, str, int, float, bool, None. Non-standard types converted via str() (see default=str).

## Returns

**Type**: `bool`

            Success: file written and closed properly.
            Failure: exception during write (logged to console).

## Algorithm

- 1. **Convert Path** (if needed):
- a. Check if filepath is string type
- b. If string, convert to Path object
- c. Ensures consistent path handling

- 2. **Try File Writing**:
- a. Enter try block for error handling
- b. Open file in write mode with UTF-8 encoding
- c. Use context manager (with) for automatic closing
- d. Call json.dump() with configuration:
  - i. indent=2 for readable formatting (2-space indent)
  - ii. default=str to convert non-serializable types to strings
  - iii. ensure_ascii=False to preserve Unicode characters
- e. Return True on successful write

- 3. **Handle Errors**:
- a. Catch any Exception during write operation
- b. Print error message to console: f"Error saving: &#123;e&#125;"
- c. Return False to indicate failure

## Interactions

- **pathlib.Path**: Path manipulation
- **json.dump()**: JSON serialization to file
- **File I/O**: Opens and writes file with UTF-8 encoding

## Example

```python
# Save dictionary
data = {'name': 'LMS', 'version': '1.0', 'active': True}
success = save_json_file('config.json', data)
print(success)
# True

# File contents (formatted):
# {
#   "name": "LMS",
#   "version": "1.0",
#   "active": true
# }

# Save list
assignments = [
    {'id': 1, 'title': 'Assignment 1'},
    {'id': 2, 'title': 'Assignment 2'}
    ]
success = save_json_file('assignments.json', assignments)

# Save with datetime (converted to string)
from datetime import datetime
data = {'timestamp': datetime.now()}
success = save_json_file('log.json', data)
# timestamp field becomes string representation

# Handle write error (e.g., permission denied)
success = save_json_file('/root/protected.json', data)
print(success)
# False
# Console output: "Error saving: [Errno 13] Permission denied..."
```

## See Also

- `load_json_file()`: Load data from JSON file
- `json`: Python JSON module
- `pathlib.Path`: Path manipulation

## Notes

- Creates file if doesn't exist
- Overwrites existing file content
- 2-space indentation for readability
- default=str converts datetime, custom objects to strings
- ensure_ascii=False preserves Unicode (emoji, non-Latin chars)
- UTF-8 encoding for universal compatibility
- Thread-safe writing with context manager
- Prints errors to console (no exception raised)
- Returns bool for caller error handling
