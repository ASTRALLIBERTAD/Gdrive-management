---
id: "format_file_size"
sidebar_position: 4
title: "format_file_size"
---

# ⚙️ format_file_size

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`common.py`](./common.py) | **Line:** 249
:::

Format file size from bytes to human-readable string with units.

Converts a byte count into a formatted string with appropriate unit
suffix (B, KB, MB, GB, TB, PB). Automatically selects the most
appropriate unit for readability (e.g., 1500000 → "1.4 MB").

## Purpose

- Convert raw byte counts to human-readable format
        - Automatically select appropriate size unit
        - Format with one decimal place precision
        - Handle edge cases (None, invalid input)

## Parameters

- **`size_bytes`** (int | None): File size in bytes. Can be integer, numeric string convertible to int, or None. Negative values treated as errors. None indicates unknown size.

## Returns

**Type**: `str`

            - "1.5 MB", "500 B", "2.3 GB"
            - "Unknown size" if input None or invalid

## Algorithm

- 1. **Check for None**:
- a. If size_bytes is None:
  - i. Return "Unknown size" immediately

- 2. **Try Conversion and Formatting**:
- a. Enter try block for error handling
- b. Convert size_bytes to integer: int(size_bytes)
- c. Store in size variable (float for division)

- 3. **Iterate Through Units**:
- a. Define units list: ['B', 'KB', 'MB', 'GB', 'TB']
- b. For each unit in list:
  - i. Check if size < 1024.0
  - ii. If True:
    - - Format: f"&#123;size:.1f&#125; &#123;unit&#125;"
    - - Return formatted string immediately
  - iii. If False:
    - - Divide size by 1024.0
    - - Continue to next unit

- 4. **Handle Petabytes** (very large files):
- a. If loop completes without return:
  - i. Size ≥ 1024 TB
  - ii. Format as petabytes: f"&#123;size:.1f&#125; PB"
  - iii. Return formatted string

- 5. **Handle Errors**:
- a. Catch ValueError (invalid string) or TypeError (invalid type)
- b. Return "Unknown size"

## Interactions

- **int()**: Converts input to integer
- **String formatting**: f-strings with .1f precision

## Example

```python
# Small file (bytes)
format_file_size(500)
# '500.0 B'

# Kilobytes
format_file_size(1536)
# '1.5 KB'

# Megabytes
format_file_size(1572864)
# '1.5 MB'

# Gigabytes
format_file_size(1610612736)
# '1.5 GB'

# None input
format_file_size(None)
# 'Unknown size'

# Invalid input
format_file_size("invalid")
# 'Unknown size'

# String numeric input
format_file_size("2048")
# '2.0 KB'
```

## See Also

- `DriveService`: Uses this for file size display
- `os.path`: File size retrieval

## Notes

- Uses 1024 divisor (binary units, not decimal)
- One decimal place precision for all units
- Handles input types: int, numeric string, None
- Returns "Unknown size" for None or invalid input
- Supports sizes up to petabytes (PB)
- No negative size handling (treats as error)
- Thread-safe (no state modification)
