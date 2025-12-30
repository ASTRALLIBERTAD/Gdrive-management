---
id: "filepreviewservice"
sidebar_position: 2
title: "FilePreviewService"
---

# 📦 FilePreviewService

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Completeness](https://img.shields.io/badge/Docs-20%25-red)

:::info Source
**File:** [`file_preview_service.py`](./file_preview_service.py) | **Line:** 23
:::

Service for generating and displaying file previews across multiple formats.

FilePreviewService provides a comprehensive file preview system that fetches
files from local filesystem or Google Drive, detects file types, and renders
appropriate preview widgets in modal overlays. It supports images, text files,
PDFs, Microsoft Office documents, and provides fallback handling for unsupported
formats with download and browser viewing options.
The service implements a plugin-style architecture where each file type has
a dedicated rendering method, allowing for easy extension with new format
support. It handles binary/text detection, size calculations, error states,
and user interactions (download, open in browser) within a unified interface.

## Purpose

- Display file previews in modal overlay dialogs
        - Support multiple file formats (images, text, PDFs, Office docs)
        - Fetch files from Google Drive or local filesystem
        - Provide download functionality for all file types
        - Enable browser viewing for Drive-hosted files
        - Handle errors gracefully with user-friendly messages
        - Calculate and display file sizes

## Attributes

- **`page`** (ft.Page): Flet page instance for UI rendering and overlay management. Provides access to page.overlay list and page.update() for UI refresh.
- **`drive_service`** (DriveService or None): Google Drive service for fetching Drive-hosted files. If None, only local file preview available. Provides get_file_info() and files().get_media() access.
- **`current_overlay`** (ft.Control or None): Reference to currently displayed preview overlay container. Used for cleanup when closing preview. None when no preview is active.

## Interactions

- **DriveService**: Fetches Drive file metadata and content
- **googleapiclient.http.MediaIoBaseDownload**: Downloads Drive files
- **ft.Page**: Manages overlay display and page updates
- **base64**: Encodes binary data for image display
- **mimetypes**: Detects file types from extensions
- **io.BytesIO**: Buffers file downloads in memory
- **webbrowser**: Opens files in system browser
- **pathlib.Path**: Handles download directory operations
- Algorithm (High-Level Workflow):
- *Phase 1: Preview Initiation**
- 1. User requests preview with file_id or file_path
- 2. Create loading overlay with progress indicator
- 3. Build overlay structure (header, close button, content area)
- 4. Add overlay to page.overlay and display
- 5. Route to appropriate loading method based on source
- *Phase 2: File Loading**
- a. **From Drive** (_load_from_drive):
- i. Fetch file metadata for MIME type
- ii. Create download request
- iii. Stream file content to BytesIO buffer
- iv. Read buffer to bytes
- b. **From Local** (_load_from_path):
- i. Guess MIME type from extension
- ii. Open file in binary mode
- iii. Read entire file to bytes
- *Phase 3: Preview Rendering** (_render_preview)
- 1. Calculate file size in MB
- 2. Match MIME type to format category:
- image/* → _create_image_preview
- application/pdf → _create_pdf_preview
- text/* → _create_text_preview
- MS Office → format-specific preview
- Other → _create_default_preview
- 3. Generate preview widget with file info
- 4. Update overlay content container
- 5. Refresh page to display
- *Phase 4: User Interaction**
- 1. User views preview in overlay
- 2. Available actions:
- Close button → remove overlay
- Download button → save to Downloads folder
- Open in Browser → launch Drive web view
- *Phase 5: Cleanup**
- 1. User closes preview
- 2. Remove overlay from page.overlay
- 3. Clear current_overlay reference
- 4. Update page

## Example

```python
# Initialize service
from services.file_preview_service import FilePreviewService
preview_service = FilePreviewService(page, drive_service)

# Preview Drive file
preview_service.show_preview(
    file_id='1abc...xyz',
    file_name='document.pdf'
    )
# Modal overlay displays with PDF preview

# Preview local file
preview_service.show_preview(
    file_path='/path/to/image.png',
    file_name='image.png'
    )
# Image rendered in overlay

# Close preview programmatically
preview_service.close_preview()

# Supported formats:
# - Images: PNG, JPEG, GIF, WebP (rendered inline)
# - Text: TXT, CSV, JSON, XML, code files (scrollable text)
# - PDFs: Placeholder with download/open options
# - Office: Word, Excel, PowerPoint placeholders
# - Archives: ZIP, RAR, 7Z with download option
# - Media: Video, audio placeholders
```

## See Also

- `DriveService`: File source for Drive files
- `SubmissionManager`: Uses previews
- `googleapiclient.http.MediaIoBaseDownload`: Drive download handler
- `base64`: Image encoding for display
- `mimetypes`: File type detection

## Notes

- Modal overlay blocks interaction with page content
- Images rendered inline using base64 encoding
- Text files limited by memory (no streaming)
- PDF/Office docs show placeholders (no embedded viewer)
- Download saves to system Downloads folder
- File naming conflicts handled with (1), (2) suffixes
- Browser opening requires Drive file_id
- Overlay automatically sized for content
- Close button and semi-transparent backdrop
- Error states show friendly messages with fallback options

## References

- Flet Overlays: [https://flet.dev/docs/controls/page#overlay](https://flet.dev/docs/controls/page#overlay)
- MIME Types: [https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types)
- Base64 Encoding: [https://docs.python.org/3/library/base64.html](https://docs.python.org/3/library/base64.html)
