---
id: "load_json_file"
sidebar_position: 2
title: "load_json_file"
---

# ⚙️ load_json_file

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`common.py`](./common.py) | **Line:** 14
:::

Load and parse a JSON file with error handling and default fallback.

Reads a JSON file from the filesystem, parses its contents, and returns
the parsed data structure. Provides robust error handling for missing
files, malformed JSON, and encoding issues, returning a default value
when errors occur.

## Purpose

- Safely load JSON data from filesystem
        - Handle missing files gracefully with defaults
        - Parse JSON content into Python data structures
        - Provide error resilience for I/O and parsing failures

## Parameters

- **`filepath`** (str | Path): Path to the JSON file to load. Can be either a string path or pathlib.Path object. Automatically converts strings to Path objects for consistent handling.
- **`default`** (any, optional): Value to return if file doesn't exist, cannot be read, or contains invalid JSON. If None, defaults to empty list []. Can be any Python object (list, dict, None, etc.). Defaults to None.

## Returns

**Type**: `any`

            Returns default value if file missing or parsing fails.

## Algorithm

- 1. **Convert Path** (if needed):
- a. Check if filepath is string type
- b. If string, convert to Path object
- c. Ensures consistent path handling

- 2. **Check File Existence**:
- a. Call filepath.exists() to verify file present
- b. If file doesn't exist, skip to step 5

- 3. **Try File Reading and Parsing**:
- a. Enter try block for error handling
- b. Open file with UTF-8 encoding
- c. Use context manager (with) for automatic closing
- d. Call json.load(f) to parse JSON content
- e. Return parsed data immediately on success

- 4. **Handle Errors**:
- a. Catch any exception (IOError, JSONDecodeError, etc.)
- b. Pass silently (no error logging)
- c. Fall through to default return

- 5. **Return Default**:
- a. If default parameter is not None:
  - i. Return provided default value
- b. If default is None:
  - i. Return empty list []
- c. Provides safe fallback for missing/invalid files

## Interactions

- **pathlib.Path**: Path manipulation and existence checking
- **json.load()**: JSON parsing from file object
- **File I/O**: Opens and reads file with UTF-8 encoding

## Example

```python
# Load existing JSON file
data = load_json_file('config.json')
print(data)
# {'setting1': 'value1', 'setting2': 42}

# File doesn't exist, returns default (empty list)
data = load_json_file('missing.json')
print(data)
# []

# Custom default value
data = load_json_file('missing.json', default={'key': 'value'})
print(data)
# {'key': 'value'}

# Path object input
from pathlib import Path
data = load_json_file(Path('data.json'))

# Malformed JSON returns default
# File contains: {invalid json}
data = load_json_file('malformed.json', default=None)
print(data)
# None
```

## See Also

- `save_json_file()`: Save data to JSON file
- `json`: Python JSON module
- `pathlib.Path`: Path manipulation

## Notes

- Automatically converts string paths to Path objects
- Uses UTF-8 encoding for universal compatibility
- Silent error handling (no exceptions raised)
- Default value of None results in empty list return
- Suitable for configuration files and data persistence
- Thread-safe file reading with context manager
- Does not create file if missing
