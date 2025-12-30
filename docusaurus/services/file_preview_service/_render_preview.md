---
id: "_render_preview"
sidebar_position: 7
title: "_render_preview"
---

# ⚙️ _render_preview

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`file_preview_service.py`](./file_preview_service.py) | **Line:** 654
:::

Select and render appropriate preview widget based on file type.

Analyzes file MIME type and dispatches to format-specific rendering method.
Calculates file size and creates preview with metadata display.

## Parameters

- **`file_data`** (bytes): Raw file content as bytes. Can be any size but large files (>50MB) may impact performance.
- **`mime_type`** (str or None): MIME type of file (e.g., 'image/png', 'text/plain'). Used for format detection. None if unknown.
- **`file_name`** (str): Display name for file. Shown in preview and used for extension detection as fallback.
- **`container`** (ft.Container): Target container to update with preview. Currently contains loading state.
- **`file_id`** (str, optional): Google Drive file ID for browser links. None for local files. Enables "Open in Browser" button. Defaults to None.
- **`close_callback`** (Callable, optional): Function to close overlay. Signature: (e: ft.ControlEvent) -> None. Not currently used but available for future features. Defaults to None.

## Returns

**Type**: `None`

                page.update() as side effects.

## Algorithm

- 1. **Calculate File Size**:
    - a. Get length in bytes: len(file_data)
    - b. Divide by 1024 twice: / (1024 * 1024)
    - c. Store in size_mb as float
    - d. Used for display in all preview types

  - 2. **Match MIME Type to Renderer**:
    - a. If mime_type starts with 'image/':
    - i. Call _create_image_preview(file_data, size_mb)
    - ii. Renders inline image

    - b. Elif mime_type == 'application/pdf':
    - i. Call _create_pdf_preview(file_data, file_name, size_mb, file_id)
    - ii. Shows PDF placeholder with actions

    - c. Elif mime_type starts with 'text/':
    - i. Call _create_text_preview(file_data, size_mb)
    - ii. Displays text content in scrollable area

    - d. Elif mime_type in MS Word types:
    - i. Types: 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    - ii. Call _create_word_preview(file_data, file_name, size_mb, file_id)
    - iii. Shows Word placeholder

    - e. Elif mime_type in Excel types:
    - i. Types: 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    - ii. Call _create_excel_preview(file_data, file_name, size_mb, file_id)
    - iii. Shows Excel placeholder

    - f. Elif mime_type in PowerPoint types:
    - i. Types: 'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    - ii. Call _create_powerpoint_preview(file_data, file_name, size_mb, file_id)
    - iii. Shows PowerPoint placeholder

    - g. Else (unknown or unsupported type):
    - i. Call _create_default_preview(file_data, file_name, mime_type, size_mb, file_id)
    - ii. Generic file placeholder with download option

  - 3. **Wrap Preview Widget**:
    - a. Create ft.Column to wrap preview_widget
    - b. Set scroll: "auto" for large content
    - c. Set horizontal_alignment: CENTER
    - d. Set alignment: CENTER
    - e. Contains single preview widget

  - 4. **Update Container**:
    - a. Set container.content to wrapped Column
    - b. Replaces loading indicator

  - 5. **Refresh UI**:
    - a. Call self.page.update()
    - b. Renders new preview content

## Interactions

- **_create_image_preview()**: Image rendering
- **_create_pdf_preview()**: PDF placeholder
- **_create_text_preview()**: Text display
- **_create_word_preview()**: Word placeholder
- **_create_excel_preview()**: Excel placeholder
- **_create_powerpoint_preview()**: PowerPoint placeholder
- **_create_default_preview()**: Generic fallback

## Example

```python
# Internal usage from loader methods
file_data = b'...'  # Raw bytes
mime_type = 'image/png'
container = ft.Container()
preview_service._render_preview(
    file_data,
    mime_type,
    'photo.png',
    container,
    file_id='drive_id'
    )
# Container now shows image preview
```

## See Also

- `_load_from_drive()`: Calls this after download
- `_load_from_path()`: Calls this after read
- `_create_image_preview()`: Image renderer
- `_create_text_preview()`: Text renderer

## Notes

- MIME type matching in priority order
- Images rendered inline (base64)
- Text decoded as UTF-8 (may fail for binary)
- Office docs show placeholders (no embedded viewer)
- Unknown types get generic preview
- Size displayed in all preview types
- Preview widget wrapped in scrollable Column
- file_id enables browser viewing option
