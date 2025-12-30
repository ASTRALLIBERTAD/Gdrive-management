---
id: "_load_from_drive"
sidebar_position: 5
title: "_load_from_drive"
---

# ⚙️ _load_from_drive

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`file_preview_service.py`](./file_preview_service.py) | **Line:** 415
:::

Fetch and load file content from Google Drive.

Downloads file from Drive API, retrieves metadata, and renders appropriate
preview based on MIME type. Handles download progress and errors.

## Parameters

- **`file_id`** (str): Google Drive file ID to fetch. Must be valid ID from Drive with read permissions for authenticated user.
- **`file_name`** (str): Display name for file in preview. Used in preview header and error messages.
- **`container`** (ft.Container): UI container to populate with preview content. Initially contains loading state, replaced with preview widget or error message.
- **`close_callback`** (Callable): Function to close the overlay. Signature: (e: ft.ControlEvent) -> None. Called when user clicks close or on certain errors.

## Returns

**Type**: `None`


## Algorithm

- 1. **Try Loading File**:
    - a. Enter try block for error handling

  - 2. **Get File Metadata**:
    - a. Call drive_service.get_file_info(file_id)
    - b. Returns file metadata dict
    - c. Extract MIME type: file_info.get('mimeType', '')
    - d. Used for format detection

  - 3. **Create Download Request**:
    - a. Call drive_service.service.files().get_media(fileId=file_id)
    - b. Returns media download request object
    - c. Does not execute yet (lazy)

  - 4. **Initialize Download Buffer**:
    - a. Create io.BytesIO() buffer
    - b. In-memory buffer for file content
    - c. Avoids temporary files

  - 5. **Setup Downloader**:
    - a. Create MediaIoBaseDownload(file_buffer, request)
    - b. Handles chunked download
    - c. Provides progress updates

  - 6. **Download Loop**:
    - a. Set done = False
    - b. While not done:
    - i. Call downloader.next_chunk()
    - ii. Returns (status, done)
    - iii. status has progress info (not used currently)
    - iv. done = True when complete
    - c. Downloads entire file to buffer

  - 7. **Extract File Data**:
    - a. Call file_buffer.seek(0) to rewind
    - b. Call file_buffer.read() to get bytes
    - c. Store in file_data variable

  - 8. **Render Preview**:
    - a. Call _render_preview() with:
    - i. file_data: downloaded bytes
    - ii. mime_type: from metadata
    - iii. file_name: display name
    - iv. container: target container
    - v. file_id: for browser links
    - vi. close_callback: for cleanup

  - 9. **Handle Errors**:
    - a. Catch any Exception during process
    - b. Create error view with _create_error_view()
    - c. Pass error message: f"Error loading file: &#123;str(e)&#125;"
    - d. Include file_id for "Open in Browser" fallback
    - e. Update container.content with error view
    - f. Call page.update() to display error

## Interactions

- **DriveService.get_file_info()**: Fetches metadata
- **DriveService.service.files().get_media()**: Creates download request
- **MediaIoBaseDownload**: Handles chunked download
- **io.BytesIO**: Buffers file content
- **_render_preview()**: Renders file preview
- **_create_error_view()**: Creates error UI

## Example

```python
# Internal usage from show_preview
container = ft.Container()
def close_fn(e):
    # Close overlay
preview_service._load_from_drive(
    'file_id',
    'document.pdf',
    container,
    close_fn
    )
# Container updated with PDF preview
```

## See Also

- `show_preview()`: Calls this for Drive files
- `_render_preview()`: Renders loaded content
- `_create_error_view()`: Error display
- `googleapiclient.http.MediaIoBaseDownload`: Download handler

## Notes

- Downloads entire file to memory (no streaming)
- Progress updates not displayed (could be added)
- MIME type from metadata (more reliable than extension)
- BytesIO buffer avoids temporary files
- Errors show fallback "Open in Browser" option
- File must be accessible to authenticated user
