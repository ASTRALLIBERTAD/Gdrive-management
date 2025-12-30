---
id: "_load_from_path"
sidebar_position: 6
title: "_load_from_path"
---

# ⚙️ _load_from_path

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`file_preview_service.py`](./file_preview_service.py) | **Line:** 555
:::

Load file content from local filesystem.

Reads file from disk, detects MIME type, and renders preview. Handles
file read errors and encoding issues.

## Parameters

- **`file_path`** (str): Absolute or relative path to local file. File must exist and be readable by application.
- **`file_name`** (str): Display name for file in preview header and messages.
- **`container`** (ft.Container): Target container to populate with preview content. Initially contains loading state.
- **`close_callback`** (Callable): Function to close overlay. Signature: (e: ft.ControlEvent) -> None. Not currently used but available for future enhancements.

## Returns

**Type**: `None`


## Algorithm

- 1. **Try Loading File**:
    - a. Enter try block for error handling

  - 2. **Guess MIME Type**:
    - a. Call mimetypes.guess_type(file_path)
    - b. Returns (mime_type, encoding) tuple
    - c. Extract mime_type (may be None)
    - d. Based on file extension

  - 3. **Open File**:
    - a. Open file_path in binary mode ('rb')
    - b. Use context manager (with) for automatic closing
    - c. Call f.read() to read entire content
    - d. Store in file_data as bytes

  - 4. **Render Preview**:
    - a. Call _render_preview() with:
    - i. file_data: read bytes
    - ii. mime_type: guessed type (may be None)
    - iii. file_name: display name
    - iv. container: target container
    - v. file_id: None (local file, no Drive ID)
    - vi. close_callback: cleanup function

  - 5. **Handle Errors**:
    - a. Catch any Exception during read
    - b. Examples: FileNotFoundError, PermissionError, OSError
    - c. Create error view with _create_error_view()
    - d. Pass error message: f"Error loading file: &#123;str(e)&#125;"
    - e. No file_id (local file has no browser option)
    - f. Update container.content with error view
    - g. Call page.update() to display error

## Interactions

- **mimetypes.guess_type()**: MIME type detection
- **File I/O**: Opens and reads file
- **_render_preview()**: Renders file content
- **_create_error_view()**: Error display

## Example

```python
# Internal usage from show_preview
container = ft.Container()
def close_fn(e):
    # Close overlay
preview_service._load_from_path(
    'C:/docs/report.txt',
    'report.txt',
    container,
    close_fn
    )
# Container updated with text preview
```

## See Also

- `show_preview()`: Calls this for local files
- `_render_preview()`: Renders loaded content
- `_create_error_view()`: Error display
- `mimetypes`: MIME type detection

## Notes

- Reads entire file to memory (no streaming)
- MIME type guessed from extension (may be inaccurate)
- Binary mode ensures correct data for all file types
- Local files have no "Open in Browser" option
- File must exist and be readable
- Large files (>100MB) may cause memory issues
