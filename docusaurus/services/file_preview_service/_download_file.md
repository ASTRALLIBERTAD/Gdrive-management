---
id: "_download_file"
sidebar_position: 16
title: "_download_file"
---

# ⚙️ _download_file

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`file_preview_service.py`](./file_preview_service.py) | **Line:** 1484
:::

Save file content to Downloads folder with duplicate handling.

Writes binary file data to user's Downloads directory. Handles filename
conflicts by appending (1), (2), etc. Shows success/failure feedback.

## Parameters

- **`file_data`** (bytes): Complete file content to save.
- **`file_name`** (str): Target filename including extension.

## Returns

**Type**: `None`


## Algorithm

- 1. **Try File Save**:
    - a. Enter try block for error handling
    - b. Import Path from pathlib

  - 2. **Build Download Path**:
    - a. Get home directory: Path.home()
    - b. Append Downloads subfolder
    - c. Append file_name
    - d. Store in downloads_path

  - 3. **Handle Name Conflicts**:
    - a. Set counter = 1
    - b. Store original_path = downloads_path
    - c. While downloads_path.exists():
    - i. Split into stem and suffix (name and extension)
    - ii. Build new path: "&#123;name&#125; (&#123;counter&#125;)&#123;ext&#125;"
    - iii. Increment counter
    - iv. Repeat until unique path found

  - 4. **Write File**:
    - a. Open downloads_path in binary write mode ('wb')
    - b. Use context manager for automatic closing
    - c. Write file_data: f.write(file_data)

  - 5. **Show Success**:
    - a. Format message: f"✓ Downloaded to: &#123;downloads_path.name&#125;"
    - b. Call _show_snackbar(message, GREEN)

  - 6. **Handle Errors**:
    - a. Catch any Exception during save
    - b. Format error: f"✗ Download failed: &#123;str(e)&#125;"
    - c. Call _show_snackbar(error, RED)

## Interactions

- **pathlib.Path**: File path operations
- **File I/O**: Writes file to disk
- **_show_snackbar()**: User feedback

## Example

```python
# Download file
file_data = b'content...'
preview_service._download_file(file_data, 'document.pdf')
# Saves to ~/Downloads/document.pdf
# Shows "✓ Downloaded to: document.pdf"

# Duplicate filename
preview_service._download_file(file_data, 'document.pdf')
# Saves to ~/Downloads/document (1).pdf
# Shows "✓ Downloaded to: document (1).pdf"
```

## See Also

- `_create_pdf_preview()`: Provides download button
- `_show_snackbar()`: Feedback display

## Notes

- Saves to Downloads folder only
- Auto-handles filename conflicts
- Counter appended in format: "file (1).ext"
- Green snackbar for success
- Red snackbar for errors
- Entire file written at once (not chunked)
