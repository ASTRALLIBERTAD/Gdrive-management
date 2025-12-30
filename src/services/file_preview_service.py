"""File Preview Service Module.

This module provides a service for previewing various file types within the app.
It handles fetching file content (local or Drive), detecting mime types,
and rendering appropriate preview widgets (image, text, or placeholders).

Classes:
    FilePreviewService: Manages file preview generation and display.

See Also:
    :class:`~src.services.drive_service.DriveService`: Source for Drive files.
"""

import flet as ft
import base64
import mimetypes
import io
from googleapiclient.http import MediaIoBaseDownload
from utils.common import show_snackbar


class FilePreviewService:
    """Service for generating and displaying file previews across multiple formats.

    FilePreviewService provides a comprehensive file preview system that fetches
    files from local filesystem or Google Drive, detects file types, and renders
    appropriate preview widgets in modal overlays. It supports images, text files,
    PDFs, Microsoft Office documents, and provides fallback handling for unsupported
    formats with download and browser viewing options.
    
    The service implements a plugin-style architecture where each file type has
    a dedicated rendering method, allowing for easy extension with new format
    support. It handles binary/text detection, size calculations, error states,
    and user interactions (download, open in browser) within a unified interface.

    Purpose:
        - Display file previews in modal overlay dialogs
        - Support multiple file formats (images, text, PDFs, Office docs)
        - Fetch files from Google Drive or local filesystem
        - Provide download functionality for all file types
        - Enable browser viewing for Drive-hosted files
        - Handle errors gracefully with user-friendly messages
        - Calculate and display file sizes

    Attributes:
        page (ft.Page): Flet page instance for UI rendering and overlay management.
            Provides access to page.overlay list and page.update() for UI refresh.
        drive_service (DriveService or None): Google Drive service for fetching
            Drive-hosted files. If None, only local file preview available.
            Provides get_file_info() and files().get_media() access.
        current_overlay (ft.Control or None): Reference to currently displayed
            preview overlay container. Used for cleanup when closing preview.
            None when no preview is active.

    Interactions:
        - **DriveService**: Fetches Drive file metadata and content
        - **googleapiclient.http.MediaIoBaseDownload**: Downloads Drive files
        - **ft.Page**: Manages overlay display and page updates
        - **base64**: Encodes binary data for image display
        - **mimetypes**: Detects file types from extensions
        - **io.BytesIO**: Buffers file downloads in memory
        - **webbrowser**: Opens files in system browser
        - **pathlib.Path**: Handles download directory operations

    Algorithm (High-Level Workflow):
        **Phase 1: Preview Initiation**
            1. User requests preview with file_id or file_path
            2. Create loading overlay with progress indicator
            3. Build overlay structure (header, close button, content area)
            4. Add overlay to page.overlay and display
            5. Route to appropriate loading method based on source
        
        **Phase 2: File Loading**
            a. **From Drive** (_load_from_drive):
               i. Fetch file metadata for MIME type
               ii. Create download request
               iii. Stream file content to BytesIO buffer
               iv. Read buffer to bytes
            b. **From Local** (_load_from_path):
               i. Guess MIME type from extension
               ii. Open file in binary mode
               iii. Read entire file to bytes
        
        **Phase 3: Preview Rendering** (_render_preview)
            1. Calculate file size in MB
            2. Match MIME type to format category:
               - image/* → _create_image_preview
               - application/pdf → _create_pdf_preview
               - text/* → _create_text_preview
               - MS Office → format-specific preview
               - Other → _create_default_preview
            3. Generate preview widget with file info
            4. Update overlay content container
            5. Refresh page to display
        
        **Phase 4: User Interaction**
            1. User views preview in overlay
            2. Available actions:
               - Close button → remove overlay
               - Download button → save to Downloads folder
               - Open in Browser → launch Drive web view
        
        **Phase 5: Cleanup**
            1. User closes preview
            2. Remove overlay from page.overlay
            3. Clear current_overlay reference
            4. Update page

    Example:
        >>> # Initialize service
        >>> from services.file_preview_service import FilePreviewService
        >>> preview_service = FilePreviewService(page, drive_service)
        >>> 
        >>> # Preview Drive file
        >>> preview_service.show_preview(
        ...     file_id='1abc...xyz',
        ...     file_name='document.pdf'
        ... )
        >>> # Modal overlay displays with PDF preview
        >>> 
        >>> # Preview local file
        >>> preview_service.show_preview(
        ...     file_path='/path/to/image.png',
        ...     file_name='image.png'
        ... )
        >>> # Image rendered in overlay
        >>> 
        >>> # Close preview programmatically
        >>> preview_service.close_preview()
        >>> 
        >>> # Supported formats:
        >>> # - Images: PNG, JPEG, GIF, WebP (rendered inline)
        >>> # - Text: TXT, CSV, JSON, XML, code files (scrollable text)
        >>> # - PDFs: Placeholder with download/open options
        >>> # - Office: Word, Excel, PowerPoint placeholders
        >>> # - Archives: ZIP, RAR, 7Z with download option
        >>> # - Media: Video, audio placeholders

    See Also:
        - :class:`~services.drive_service.DriveService`: File source for Drive files
        - :class:`~ui.todo_modules.submission_manager.SubmissionManager`: Uses previews
        - :class:`googleapiclient.http.MediaIoBaseDownload`: Drive download handler
        - :mod:`base64`: Image encoding for display
        - :mod:`mimetypes`: File type detection

    Notes:
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

    Supported File Types:
        - **Images**: PNG, JPEG, GIF, WebP, BMP, SVG
        - **Text**: TXT, CSV, JSON, XML, HTML, CSS, JS, Python, etc.
        - **Documents**: PDF, DOCX, DOC, XLSX, XLS, PPTX, PPT
        - **Archives**: ZIP, RAR, 7Z, TAR, GZ
        - **Media**: MP4, AVI, MOV, MP3, WAV, FLAC
        - **Other**: Generic placeholder for all other types

    Performance Considerations:
        - Large files loaded entirely into memory
        - Images base64-encoded (increases memory 33%)
        - Text files decoded as UTF-8 (may fail for binary)
        - No streaming for large files (consider for >50MB)
        - Download writes to disk asynchronously

    References:
        - Flet Overlays: https://flet.dev/docs/controls/page#overlay
        - MIME Types: https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types
        - Base64 Encoding: https://docs.python.org/3/library/base64.html
    """

    def __init__(self, page: ft.Page, drive_service=None):
        """Initialize FilePreviewService with page and optional Drive service.

        Sets up the preview service with UI context and file access capabilities.
        Prepares for displaying previews without creating any UI elements yet.

        Args:
            page (ft.Page): Flet page instance for displaying overlays and managing
                UI updates. Must be active and rendered. Provides access to
                page.overlay list for modal display.
            drive_service (DriveService, optional): Google Drive service wrapper
                for fetching Drive-hosted files. If None, only local file preview
                available. Must be authenticated if provided. Defaults to None.

        Algorithm:
            1. **Store Page Reference**:
               a. Assign page parameter to self.page
               b. Used for overlay management and UI updates
            
            2. **Store Drive Service**:
               a. Assign drive_service to self.drive_service
               b. May be None if Drive integration unavailable
            
            3. **Initialize Overlay State**:
               a. Set self.current_overlay = None
               b. No preview active initially
               c. Updated when preview displayed

        Interactions:
            - **ft.Page**: Stored for overlay and update operations

        Example:
            >>> # With Drive service
            >>> auth = GoogleAuth()
            >>> drive = DriveService(auth.get_service())
            >>> preview = FilePreviewService(page, drive)
            >>> 
            >>> # Without Drive service (local files only)
            >>> preview = FilePreviewService(page)
            >>> preview.show_preview(file_path='local.txt', file_name='local.txt')

        See Also:
            - :meth:`show_preview`: Display file preview
            - :class:`~services.drive_service.DriveService`: Drive file access

        Notes:
            - No UI created during initialization
            - current_overlay starts as None
            - drive_service optional (local files work without it)
            - Page must be active for overlay display
        """
        self.page = page
        self.drive_service = drive_service
        self.current_overlay = None
    
    def show_preview(self, file_id=None, file_path=None, file_name="File"):
        """Display file preview in modal overlay with loading state.

        Creates and displays a modal overlay containing file preview. Handles
        asynchronous loading from Drive or local filesystem with progress indicator.
        Shows file header with close button and preview content area.

        Args:
            file_id (str, optional): Google Drive file ID for Drive-hosted files.
                33-character alphanumeric string. Requires drive_service to be set.
                If provided, file loaded via Drive API. Defaults to None.
            file_path (str, optional): Absolute or relative path to local file.
                File must exist and be readable. Used when file_id not provided.
                Defaults to None.
            file_name (str, optional): Display name for file in overlay header.
                Shown with visibility icon. Can be descriptive name even if
                different from actual filename. Defaults to "File".

        Returns:
            None: Creates overlay and updates page as side effects. Preview
                displayed asynchronously after file loads.

        Algorithm:
            1. **Create Loading Container**:
               a. Build ft.Container with centered Column
               b. Add ProgressRing for loading animation
               c. Add "Loading preview..." text
               d. Set container size: 700x500
               e. Center alignment for progress indicator
            
            2. **Define Close Handler**:
               a. Create close_preview(e) function
               b. Implementation:
                  i. Check if current_overlay exists and in page.overlay
                  ii. Remove overlay from page.overlay
                  iii. Set current_overlay = None
                  iv. Call page.update()
            
            3. **Build Overlay Structure**:
               a. Create header Row with:
                  i. Visibility icon (BLUE)
                  ii. File name text (size 18, bold, expandable)
                  iii. Close IconButton (calls close_preview)
               b. Add Divider separator
               c. Add content_container (loading initially)
               d. Wrap in Column (tight spacing)
            
            4. **Style Overlay Container**:
               a. Set padding: 20px
               b. Set bgcolor: WHITE
               c. Set border_radius: 10px
               d. Set dimensions: 750x600
               e. Add shadow effect (blur 20, opacity 0.3)
            
            5. **Create Modal Background**:
               a. Center inner container
               b. Set expand: True (full screen)
               c. Set backdrop: semi-transparent BLACK (opacity 0.5)
               d. Prevent click-through (on_click: lambda e: None)
            
            6. **Display Overlay**:
               a. Append overlay to page.overlay list
               b. Store in self.current_overlay
               c. Call page.update() to render
            
            7. **Route to Loader**:
               a. If file_id provided AND drive_service exists:
                  i. Call _load_from_drive() with parameters
                  ii. Async load from Drive
               b. Elif file_path provided:
                  i. Call _load_from_path() with parameters
                  ii. Sync load from filesystem
               c. Else (neither provided):
                  i. Update content_container with error
                  ii. Show "No file to preview" message with error icon
                  iii. Call page.update()

        Interactions:
            - **ft.Container, ft.Column, ft.Row**: UI structure
            - **ft.ProgressRing**: Loading indicator
            - **ft.IconButton**: Close button
            - **page.overlay**: Modal display
            - **_load_from_drive()**: Drive file loading
            - **_load_from_path()**: Local file loading

        Example:
            >>> # Preview Drive file
            >>> preview_service.show_preview(
            ...     file_id='1abc...xyz',
            ...     file_name='Assignment.pdf'
            ... )
            >>> # Overlay shows with loading spinner
            >>> # Then PDF preview or placeholder
            >>> 
            >>> # Preview local file
            >>> preview_service.show_preview(
            ...     file_path='C:/docs/report.txt',
            ...     file_name='Report'
            ... )
            >>> 
            >>> # Error case (no file specified)
            >>> preview_service.show_preview(file_name='Unknown')
            >>> # Shows "No file to preview" error

        See Also:
            - :meth:`_load_from_drive`: Drive file loading
            - :meth:`_load_from_path`: Local file loading
            - :meth:`close_preview`: Close overlay programmatically

        Notes:
            - Loading state shown immediately
            - Actual preview loaded asynchronously
            - Close button always available
            - Modal blocks page interaction
            - Backdrop click does not close (explicit close required)
            - Overlay sized for typical documents (750x600)
            - Content container updated when file loads
        """
        content_container = ft.Container(
            content=ft.Column([
                ft.ProgressRing(),
                ft.Text("Loading preview...", size=14)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=700,
            height=500,
            alignment=ft.alignment.center
        )
        
        def close_preview(e):
            if self.current_overlay and self.current_overlay in self.page.overlay:
                self.page.overlay.remove(self.current_overlay)
                self.current_overlay = None
                self.page.update()
        
        self.current_overlay = ft.Container(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.VISIBILITY, size=24, color=ft.Colors.BLUE),
                        ft.Text(file_name, size=18, weight=ft.FontWeight.BOLD, expand=True),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            on_click=close_preview,
                            tooltip="Close preview"
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(height=1),
                    content_container
                ], tight=True, spacing=10),
                padding=20,
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                width=750,
                height=600,
                shadow=ft.BoxShadow(
                    blur_radius=20,
                    color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK)
                )
            ),
            alignment=ft.alignment.center,
            expand=True,
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
            on_click=lambda e: None 
        )
        
        self.page.overlay.append(self.current_overlay)
        self.page.update()
        
        
        if file_id and self.drive_service:
            self._load_from_drive(file_id, file_name, content_container, close_preview)
        elif file_path:
            self._load_from_path(file_path, file_name, content_container, close_preview)
        else:
            content_container.content = ft.Column([
                ft.Icon(ft.Icons.ERROR, size=48, color=ft.Colors.RED),
                ft.Text("No file to preview", color=ft.Colors.RED)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            self.page.update()
    
    def _load_from_drive(self, file_id, file_name, container, close_callback):
        """Fetch and load file content from Google Drive.

        Downloads file from Drive API, retrieves metadata, and renders appropriate
        preview based on MIME type. Handles download progress and errors.

        Args:
            file_id (str): Google Drive file ID to fetch. Must be valid ID from
                Drive with read permissions for authenticated user.
            file_name (str): Display name for file in preview. Used in preview
                header and error messages.
            container (ft.Container): UI container to populate with preview content.
                Initially contains loading state, replaced with preview widget
                or error message.
            close_callback (Callable): Function to close the overlay. Signature:
                (e: ft.ControlEvent) -> None. Called when user clicks close or
                on certain errors.

        Returns:
            None: Updates container.content and page as side effects.

        Algorithm:
            1. **Try Loading File**:
               a. Enter try block for error handling
            
            2. **Get File Metadata**:
               a. Call drive_service.get_file_info(file_id)
               b. Returns file metadata dict
               c. Extract MIME type: file_info.get('mimeType', '')
               d. Used for format detection
            
            3. **Create Download Request**:
               a. Call drive_service.service.files().get_media(fileId=file_id)
               b. Returns media download request object
               c. Does not execute yet (lazy)
            
            4. **Initialize Download Buffer**:
               a. Create io.BytesIO() buffer
               b. In-memory buffer for file content
               c. Avoids temporary files
            
            5. **Setup Downloader**:
               a. Create MediaIoBaseDownload(file_buffer, request)
               b. Handles chunked download
               c. Provides progress updates
            
            6. **Download Loop**:
               a. Set done = False
               b. While not done:
                  i. Call downloader.next_chunk()
                  ii. Returns (status, done)
                  iii. status has progress info (not used currently)
                  iv. done = True when complete
               c. Downloads entire file to buffer
            
            7. **Extract File Data**:
               a. Call file_buffer.seek(0) to rewind
               b. Call file_buffer.read() to get bytes
               c. Store in file_data variable
            
            8. **Render Preview**:
               a. Call _render_preview() with:
                  i. file_data: downloaded bytes
                  ii. mime_type: from metadata
                  iii. file_name: display name
                  iv. container: target container
                  v. file_id: for browser links
                  vi. close_callback: for cleanup
            
            9. **Handle Errors**:
               a. Catch any Exception during process
               b. Create error view with _create_error_view()
               c. Pass error message: f"Error loading file: {str(e)}"
               d. Include file_id for "Open in Browser" fallback
               e. Update container.content with error view
               f. Call page.update() to display error

        Interactions:
            - **DriveService.get_file_info()**: Fetches metadata
            - **DriveService.service.files().get_media()**: Creates download request
            - **MediaIoBaseDownload**: Handles chunked download
            - **io.BytesIO**: Buffers file content
            - **_render_preview()**: Renders file preview
            - **_create_error_view()**: Creates error UI

        Example:
            >>> # Internal usage from show_preview
            >>> container = ft.Container()
            >>> def close_fn(e):
            ...     # Close overlay
            >>> preview_service._load_from_drive(
            ...     'file_id',
            ...     'document.pdf',
            ...     container,
            ...     close_fn
            ... )
            >>> # Container updated with PDF preview

        See Also:
            - :meth:`show_preview`: Calls this for Drive files
            - :meth:`_render_preview`: Renders loaded content
            - :meth:`_create_error_view`: Error display
            - :class:`googleapiclient.http.MediaIoBaseDownload`: Download handler

        Notes:
            - Downloads entire file to memory (no streaming)
            - Progress updates not displayed (could be added)
            - MIME type from metadata (more reliable than extension)
            - BytesIO buffer avoids temporary files
            - Errors show fallback "Open in Browser" option
            - File must be accessible to authenticated user
        """
        
        try:
            
            file_info = self.drive_service.get_file_info(file_id)
            mime_type = file_info.get('mimeType', '')
            
            
            request = self.drive_service.service.files().get_media(fileId=file_id)
            file_buffer = io.BytesIO()
            downloader = MediaIoBaseDownload(file_buffer, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            file_buffer.seek(0)
            file_data = file_buffer.read()
            
            
            self._render_preview(file_data, mime_type, file_name, container, file_id, close_callback)
            
        except Exception as e:
            container.content = self._create_error_view(
                f"Error loading file: {str(e)}",
                file_id=file_id
            )
            self.page.update()
    
    def _load_from_path(self, file_path, file_name, container, close_callback):
        """Load file content from local filesystem.

        Reads file from disk, detects MIME type, and renders preview. Handles
        file read errors and encoding issues.

        Args:
            file_path (str): Absolute or relative path to local file. File must
                exist and be readable by application.
            file_name (str): Display name for file in preview header and messages.
            container (ft.Container): Target container to populate with preview
                content. Initially contains loading state.
            close_callback (Callable): Function to close overlay. Signature:
                (e: ft.ControlEvent) -> None. Not currently used but available
                for future enhancements.

        Returns:
            None: Updates container.content and page as side effects.

        Algorithm:
            1. **Try Loading File**:
               a. Enter try block for error handling
            
            2. **Guess MIME Type**:
               a. Call mimetypes.guess_type(file_path)
               b. Returns (mime_type, encoding) tuple
               c. Extract mime_type (may be None)
               d. Based on file extension
            
            3. **Open File**:
               a. Open file_path in binary mode ('rb')
               b. Use context manager (with) for automatic closing
               c. Call f.read() to read entire content
               d. Store in file_data as bytes
            
            4. **Render Preview**:
               a. Call _render_preview() with:
                  i. file_data: read bytes
                  ii. mime_type: guessed type (may be None)
                  iii. file_name: display name
                  iv. container: target container
                  v. file_id: None (local file, no Drive ID)
                  vi. close_callback: cleanup function
            
            5. **Handle Errors**:
               a. Catch any Exception during read
               b. Examples: FileNotFoundError, PermissionError, OSError
               c. Create error view with _create_error_view()
               d. Pass error message: f"Error loading file: {str(e)}"
               e. No file_id (local file has no browser option)
               f. Update container.content with error view
               g. Call page.update() to display error

        Interactions:
            - **mimetypes.guess_type()**: MIME type detection
            - **File I/O**: Opens and reads file
            - **_render_preview()**: Renders file content
            - **_create_error_view()**: Error display

        Example:
            >>> # Internal usage from show_preview
            >>> container = ft.Container()
            >>> def close_fn(e):
            ...     # Close overlay
            >>> preview_service._load_from_path(
            ...     'C:/docs/report.txt',
            ...     'report.txt',
            ...     container,
            ...     close_fn
            ... )
            >>> # Container updated with text preview

        See Also:
            - :meth:`show_preview`: Calls this for local files
            - :meth:`_render_preview`: Renders loaded content
            - :meth:`_create_error_view`: Error display
            - :mod:`mimetypes`: MIME type detection

        Notes:
            - Reads entire file to memory (no streaming)
            - MIME type guessed from extension (may be inaccurate)
            - Binary mode ensures correct data for all file types
            - Local files have no "Open in Browser" option
            - File must exist and be readable
            - Large files (>100MB) may cause memory issues
        """
        
        try:
            mime_type, _ = mimetypes.guess_type(file_path)
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            self._render_preview(file_data, mime_type, file_name, container, None, close_callback)
            
        except Exception as e:
            container.content = self._create_error_view(f"Error loading file: {str(e)}")
            self.page.update()
    
    def _render_preview(self, file_data, mime_type, file_name, container, file_id=None, close_callback=None):
        """Select and render appropriate preview widget based on file type.

        Analyzes file MIME type and dispatches to format-specific rendering method.
        Calculates file size and creates preview with metadata display.

        Args:
            file_data (bytes): Raw file content as bytes. Can be any size but
                large files (>50MB) may impact performance.
            mime_type (str or None): MIME type of file (e.g., 'image/png',
                'text/plain'). Used for format detection. None if unknown.
            file_name (str): Display name for file. Shown in preview and used
                for extension detection as fallback.
            container (ft.Container): Target container to update with preview.
                Currently contains loading state.
            file_id (str, optional): Google Drive file ID for browser links.
                None for local files. Enables "Open in Browser" button.
                Defaults to None.
            close_callback (Callable, optional): Function to close overlay.
                Signature: (e: ft.ControlEvent) -> None. Not currently used
                but available for future features. Defaults to None.

        Returns:
            None: Updates container.content with preview widget and calls
                page.update() as side effects.

        Algorithm:
            1. **Calculate File Size**:
               a. Get length in bytes: len(file_data)
               b. Divide by 1024 twice: / (1024 * 1024)
               c. Store in size_mb as float
               d. Used for display in all preview types
            
            2. **Match MIME Type to Renderer**:
               a. If mime_type starts with 'image/':
                  i. Call _create_image_preview(file_data, size_mb)
                  ii. Renders inline image
               
               b. Elif mime_type == 'application/pdf':
                  i. Call _create_pdf_preview(file_data, file_name, size_mb, file_id)
                  ii. Shows PDF placeholder with actions
               
               c. Elif mime_type starts with 'text/':
                  i. Call _create_text_preview(file_data, size_mb)
                  ii. Displays text content in scrollable area
               
               d. Elif mime_type in MS Word types:
                  i. Types: 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                  ii. Call _create_word_preview(file_data, file_name, size_mb, file_id)
                  iii. Shows Word placeholder
               
               e. Elif mime_type in Excel types:
                  i. Types: 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                  ii. Call _create_excel_preview(file_data, file_name, size_mb, file_id)
                  iii. Shows Excel placeholder
               
               f. Elif mime_type in PowerPoint types:
                  i. Types: 'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
                  ii. Call _create_powerpoint_preview(file_data, file_name, size_mb, file_id)
                  iii. Shows PowerPoint placeholder
               
               g. Else (unknown or unsupported type):
                  i. Call _create_default_preview(file_data, file_name, mime_type, size_mb, file_id)
                  ii. Generic file placeholder with download option
            
            3. **Wrap Preview Widget**:
               a. Create ft.Column to wrap preview_widget
               b. Set scroll: "auto" for large content
               c. Set horizontal_alignment: CENTER
               d. Set alignment: CENTER
               e. Contains single preview widget
            
            4. **Update Container**:
               a. Set container.content to wrapped Column
               b. Replaces loading indicator
            
            5. **Refresh UI**:
               a. Call self.page.update()
               b. Renders new preview content

        Interactions:
            - **_create_image_preview()**: Image rendering
            - **_create_pdf_preview()**: PDF placeholder
            - **_create_text_preview()**: Text display
            - **_create_word_preview()**: Word placeholder
            - **_create_excel_preview()**: Excel placeholder
            - **_create_powerpoint_preview()**: PowerPoint placeholder
            - **_create_default_preview()**: Generic fallback

        Example:
            >>> # Internal usage from loader methods
            >>> file_data = b'...'  # Raw bytes
            >>> mime_type = 'image/png'
            >>> container = ft.Container()
            >>> preview_service._render_preview(
            ...     file_data,
            ...     mime_type,
            ...     'photo.png',
            ...     container,
            ...     file_id='drive_id'
            ... )
            >>> # Container now shows image preview

        See Also:
            - :meth:`_load_from_drive`: Calls this after download
            - :meth:`_load_from_path`: Calls this after read
            - :meth:`_create_image_preview`: Image renderer
            - :meth:`_create_text_preview`: Text renderer

        Notes:
            - MIME type matching in priority order
            - Images rendered inline (base64)
            - Text decoded as UTF-8 (may fail for binary)
            - Office docs show placeholders (no embedded viewer)
            - Unknown types get generic preview
            - Size displayed in all preview types
            - Preview widget wrapped in scrollable Column
            - file_id enables browser viewing option
        """
        
        preview_widget = None
        size_mb = len(file_data) / (1024 * 1024)
        
        
        if mime_type and mime_type.startswith('image/'):
            preview_widget = self._create_image_preview(file_data, size_mb)
        
        
        elif mime_type == 'application/pdf':
            preview_widget = self._create_pdf_preview(file_data, file_name, size_mb, file_id)
        
        
        elif mime_type and mime_type.startswith('text/'):
            preview_widget = self._create_text_preview(file_data, size_mb)
        
        
        elif mime_type in [
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ]:
            preview_widget = self._create_word_preview(file_data, file_name, size_mb, file_id)
        
        
        elif mime_type in [
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ]:
            preview_widget = self._create_excel_preview(file_data, file_name, size_mb, file_id)
        
        elif mime_type in [
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ]:
            preview_widget = self._create_powerpoint_preview(file_data, file_name, size_mb, file_id)
        
        else:
            preview_widget = self._create_default_preview(file_data, file_name, mime_type, size_mb, file_id)
        
        container.content = ft.Column(
            [preview_widget],
            scroll="auto",
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER
        )
        self.page.update()
    
    def _create_image_preview(self, file_data, size_mb):
        """Create inline image preview widget with base64 encoding.

        Renders image directly in preview area using base64 data URI.
        Suitable for PNG, JPEG, GIF, WebP, and other image formats.

        Args:
            file_data (bytes): Raw image binary data. Any image format supported
                by browser (PNG, JPEG, GIF, WebP, BMP, SVG, etc.).
            size_mb (float): File size in megabytes for display. Calculated by
                caller from len(file_data) / (1024 * 1024).

        Returns:
            ft.Column: Widget containing image and size display. Column includes:
                - ft.Image with base64-encoded src
                - ft.Text showing file size
                Both centered horizontally.

        Algorithm:
            1. **Encode Image Data**:
               a. Call base64.b64encode(file_data)
               b. Returns base64 bytes
               c. Decode to string: .decode()
               d. Store in base64_data
            
            2. **Create Image Widget**:
               a. Instantiate ft.Image
               b. Set src_base64: base64_data (data URI)
               c. Set fit: CONTAIN (preserve aspect ratio)
               d. Set width: 650px (fits overlay)
               e. Set height: 450px (standard preview size)
               f. Set border_radius: 8px (rounded corners)
            
            3. **Create Size Text**:
               a. Format string: f"Size: {size_mb:.2f} MB"
               b. Set size: 12px (small, info text)
               c. Set color: GREY_600 (subtle)
            
            4. **Wrap in Column**:
               a. Create ft.Column with [image, size_text]
               b. Set horizontal_alignment: CENTER
               c. Return Column widget

        Interactions:
            - **base64.b64encode()**: Encodes image data
            - **ft.Image**: Displays image inline

        Example:
            >>> # Internal usage from _render_preview
            >>> image_data = b'\\x89PNG...'  # PNG file bytes
            >>> widget = preview_service._create_image_preview(
            ...     image_data,
            ...     size_mb=1.5
            ... )
            >>> # Returns Column with image and "Size: 1.50 MB"

        See Also:
            - :meth:`_render_preview`: Calls this for image MIME types
            - :mod:`base64`: Image encoding

        Notes:
            - Base64 encoding increases size by ~33%
            - Suitable for images up to ~5-10MB
            - Very large images may impact performance
            - Image fit: CONTAIN preserves aspect ratio
            - Width/height constrain maximum display size
            - Supports all browser-compatible image formats
            - No pagination for multi-page formats (e.g., TIFF)
        """
        
        base64_data = base64.b64encode(file_data).decode()
        return ft.Column([
            ft.Image(
                src_base64=base64_data,
                fit=ft.ImageFit.CONTAIN,
                width=650,
                height=450,
                border_radius=8
            ),
            ft.Text(f"Size: {size_mb:.2f} MB", size=12, color=ft.Colors.GREY_600)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    def _create_pdf_preview(self, file_data, file_name, size_mb, file_id):
        """Create PDF placeholder with download and browser viewing options.

        Shows PDF icon and metadata with action buttons. No inline PDF viewer
        (browser/external viewer required for actual content).

        Args:
            file_data (bytes): PDF binary content. Used for download functionality.
                Not rendered inline.
            file_name (str): PDF filename for display and download.
            size_mb (float): File size in megabytes for display.
            file_id (str or None): Drive file ID for browser viewing. If None,
                only download button shown.

        Returns:
            ft.Column: Widget containing PDF icon, metadata, and action buttons.
                Centered layout with:
                - PDF icon (RED, size 100)
                - "PDF Document" title
                - Size display
                - "Preview not available" notice
                - Download button
                - Open in Browser button (if file_id present)

        Algorithm:
            1. **Build Info Display**:
               a. Create RED PDF icon (PICTURE_AS_PDF, size 100)
               b. Create title: "PDF Document" (size 20, bold)
               c. Create size text: f"Size: {size_mb:.2f} MB" (size 14)
               d. Create notice: "PDF preview is not available in-app" (italic, grey)
            
            2. **Create Action Buttons**:
               a. Create Download button:
                  i. Text: "Download PDF"
                  ii. Icon: DOWNLOAD
                  iii. on_click: lambda e: _download_file(file_data, file_name)
               b. If file_id exists:
                  i. Create Open button:
                     - Text: "Open in Browser"
                     - Icon: OPEN_IN_NEW
                     - on_click: lambda e: _open_in_browser(file_id)
                     - bgcolor: BLUE
               c. If file_id is None:
                  i. Use empty Container (no browser button)
            
            3. **Layout Actions Row**:
               a. Create ft.Row with action buttons
               b. Set spacing: 10px between buttons
            
            4. **Assemble Column**:
               a. Create ft.Column with all elements
               b. Set horizontal_alignment: CENTER
               c. Set spacing: 10px between elements
               d. Return Column widget

        Interactions:
            - **_download_file()**: Saves PDF to Downloads
            - **_open_in_browser()**: Opens in Drive web viewer

        Example:
            >>> # Internal usage from _render_preview
            >>> pdf_data = b'%PDF-1.4...'
            >>> widget = preview_service._create_pdf_preview(
            ...     pdf_data,
            ...     'document.pdf',
            ...     2.5,
            ...     'drive_id'
            ... )
            >>> # Shows PDF placeholder with both buttons

        See Also:
            - :meth:`_render_preview`: Calls this for PDF MIME type
            - :meth:`_download_file`: Download handler
            - :meth:`_open_in_browser`: Browser opener

        Notes:
            - No inline PDF viewer (browser plugin required)
            - Download saves to Downloads folder
            - Browser view requires Drive file_id
            - Local PDFs only show download option
            - Icon color RED (standard PDF indicator)
            - Buttons horizontal layout with spacing
        """
        return ft.Column([
            ft.Icon(ft.Icons.PICTURE_AS_PDF, size=100, color=ft.Colors.RED),
            ft.Text("PDF Document", size=20, weight=ft.FontWeight.BOLD),
            ft.Text(f"Size: {size_mb:.2f} MB", size=14),
            ft.Text("PDF preview is not available in-app", size=12, italic=True, color=ft.Colors.GREY_600),
            ft.Container(height=20),
            ft.Row([
                ft.ElevatedButton(
                    "Download PDF",
                    icon=ft.Icons.DOWNLOAD,
                    on_click=lambda e: self._download_file(file_data, file_name)
                ),
                ft.ElevatedButton(
                    "Open in Browser",
                    icon=ft.Icons.OPEN_IN_NEW,
                    on_click=lambda e: self._open_in_browser(file_id),
                    bgcolor=ft.Colors.BLUE
                ) if file_id else ft.Container()
            ], spacing=10)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
    
    def _create_text_preview(self, file_data, size_mb):
        """Create scrollable text content preview with UTF-8 decoding.

        Displays text file content in scrollable container. Handles UTF-8
        decoding and shows error for binary files.

        Args:
            file_data (bytes): Text file binary content. Expected to be UTF-8
                encoded text. Non-UTF-8 files show decode error.
            size_mb (float): File size in megabytes for display.

        Returns:
            ft.Column: Widget containing text viewer or decode error. On success:
                - Scrollable text container (grey background)
                - Character count and size info
                On decode error:
                - Error icon (ORANGE)
                - Error message
                - Encoding notice

        Algorithm:
            1. **Try Text Decoding**:
               a. Enter try block for UTF-8 decode
               b. Call file_data.decode('utf-8')
               c. Store in text_content string
            
            2. **Build Text Viewer** (on success):
               a. Create inner Column with text:
                  i. ft.Text with text_content
                  ii. Set selectable: True (allow copy)
                  iii. Set size: 13px (readable)
                  iv. Set scroll: "auto" (for long content)
               b. Wrap in Container:
                  i. Set padding: 15px
                  ii. Set bgcolor: GREY_100 (light background)
                  iii. Set border_radius: 8px
                  iv. Set size: 650x450
                  v. Set border: 1px solid GREY_300
               c. Create info text:
                  i. Format: f"Size: {size_mb:.2f} MB | {len(text_content)} characters"
                  ii. Size: 12px, color: GREY_600
               d. Wrap in Column:
                  i. Container + info text
                  ii. horizontal_alignment: CENTER
            
            3. **Handle Decode Error**:
               a. Catch UnicodeDecodeError
               b. Create error Column:
                  i. Error icon (size 48, ORANGE)
                  ii. Text: "Cannot decode text file" (ORANGE)
                  iii. Text: "File may be binary or use unsupported encoding" (italic, size 12)
               c. Set horizontal_alignment: CENTER
            
            4. **Return Widget**:
               a. Return success Column or error Column

        Interactions:
            - **bytes.decode()**: UTF-8 text decoding
            - **ft.Text**: Text content display

        Example:
            >>> # Internal usage from _render_preview
            >>> text_data = b'Hello World\\nLine 2'
            >>> widget = preview_service._create_text_preview(
            ...     text_data,
            ...     0.001
            ... )
            >>> # Shows "Hello World" in scrollable box
            >>> 
            >>> # Binary file error
            >>> binary_data = b'\\x00\\x01\\x02\\xFF'
            >>> widget = preview_service._create_text_preview(
            ...     binary_data,
            ...     0.001
            ... )
            >>> # Shows decode error message

        See Also:
            - :meth:`_render_preview`: Calls this for text MIME types

        Notes:
            - Only supports UTF-8 encoding
            - Binary files show decode error
            - Text is selectable (copyable)
            - Scrollable for long files
            - Character count displayed
            - Light grey background for readability
            - Border for visual separation
            - Error state user-friendly
        """
        try:
            text_content = file_data.decode('utf-8')
            return ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Text(text_content, selectable=True, size=13)
                    ], scroll="auto"),
                    padding=15,
                    bgcolor=ft.Colors.GREY_100,
                    border_radius=8,
                    width=650,
                    height=450,
                    border=ft.border.all(1, ft.Colors.GREY_300)
                ),
                ft.Text(f"Size: {size_mb:.2f} MB | {len(text_content)} characters", 
                       size=12, color=ft.Colors.GREY_600)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        except UnicodeDecodeError:
            return ft.Column([
                ft.Icon(ft.Icons.ERROR, size=48, color=ft.Colors.ORANGE),
                ft.Text("Cannot decode text file", color=ft.Colors.ORANGE),
                ft.Text("File may be binary or use unsupported encoding", size=12, italic=True)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    def _create_word_preview(self, file_data, file_name, size_mb, file_id):
        """Create Microsoft Word placeholder with download and browser options.

        Shows Word icon and metadata. No inline Word viewer (requires external
        application or browser).

        Args:
            file_data (bytes): Word document binary content (.doc or .docx).
            file_name (str): Document filename for display and download.
            size_mb (float): File size in megabytes.
            file_id (str or None): Drive file ID for browser viewing.

        Returns:
            ft.Column: Placeholder widget with Word icon, metadata, and actions.

        Algorithm:
            1. **Build Info Display**:
               a. BLUE DESCRIPTION icon (size 100)
               b. Title: "Word Document" (size 20, bold)
               c. Size text: f"Size: {size_mb:.2f} MB"
               d. Notice: "Word preview is not available in-app" (italic, grey)
               e. Advice: "Download to view full content" (size 12, grey)
            
            2. **Create Action Buttons**:
               a. Download button → _download_file()
               b. Open in Browser button (if file_id) → _open_in_browser()
            
            3. **Layout and Return**:
               a. Vertical Column layout
               b. Centered alignment
               c. 10px spacing

        See Also:
            - :meth:`_create_pdf_preview`: Similar structure
            - :meth:`_download_file`: Download handler
            - :meth:`_open_in_browser`: Browser opener

        Notes:
            - Supports both .doc and .docx
            - No inline rendering (complex format)
            - BLUE icon (standard Word color)
            - Download for local viewing
            - Browser opens Drive Docs viewer if available
        """
        return ft.Column([
            ft.Icon(ft.Icons.DESCRIPTION, size=100, color=ft.Colors.BLUE),
            ft.Text("Word Document", size=20, weight=ft.FontWeight.BOLD),
            ft.Text(f"Size: {size_mb:.2f} MB", size=14),
            ft.Text("Word preview is not available in-app", size=12, italic=True, color=ft.Colors.GREY_600),
            ft.Text("Download to view full content", size=12, color=ft.Colors.GREY_600),
            ft.Container(height=20),
            ft.Row([
                ft.ElevatedButton(
                    "Download Document",
                    icon=ft.Icons.DOWNLOAD,
                    on_click=lambda e: self._download_file(file_data, file_name)
                ),
                ft.ElevatedButton(
                    "Open in Browser",
                    icon=ft.Icons.OPEN_IN_NEW,
                    on_click=lambda e: self._open_in_browser(file_id),
                    bgcolor=ft.Colors.BLUE
                ) if file_id else ft.Container()
            ], spacing=10)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
    
    def _create_excel_preview(self, file_data, file_name, size_mb, file_id):
        """Create Microsoft Excel placeholder with download and browser options.

        Shows Excel icon and metadata. No inline spreadsheet viewer.

        Args:
            file_data (bytes): Excel file binary content (.xls or .xlsx).
            file_name (str): Spreadsheet filename for display and download.
            size_mb (float): File size in megabytes.
            file_id (str or None): Drive file ID for browser viewing.

        Returns:
            ft.Column: Placeholder widget with Excel icon, metadata, and actions.

        Algorithm:
            Similar to _create_word_preview but with:
            - GREEN TABLE_CHART icon
            - Title: "Spreadsheet Document"
            - Download button: "Download Spreadsheet"
            - GREEN Open button color

        See Also:
            - :meth:`_create_word_preview`: Similar structure

        Notes:
            - Supports both .xls and .xlsx
            - GREEN icon (standard Excel color)
            - No inline grid viewer
        """
        return ft.Column([
            ft.Icon(ft.Icons.TABLE_CHART, size=100, color=ft.Colors.GREEN),
            ft.Text("Spreadsheet Document", size=20, weight=ft.FontWeight.BOLD),
            ft.Text(f"Size: {size_mb:.2f} MB", size=14),
            ft.Text("Spreadsheet preview is not available in-app", size=12, italic=True, color=ft.Colors.GREY_600),
            ft.Container(height=20),
            ft.Row([
                ft.ElevatedButton(
                    "Download Spreadsheet",
                    icon=ft.Icons.DOWNLOAD,
                    on_click=lambda e: self._download_file(file_data, file_name)
                ),
                ft.ElevatedButton(
                    "Open in Browser",
                    icon=ft.Icons.OPEN_IN_NEW,
                    on_click=lambda e: self._open_in_browser(file_id),
                    bgcolor=ft.Colors.GREEN
                ) if file_id else ft.Container()
            ], spacing=10)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
    
    def _create_powerpoint_preview(self, file_data, file_name, size_mb, file_id):
        """Create Microsoft PowerPoint placeholder with download and browser options.

        Shows PowerPoint icon and metadata. No inline presentation viewer.

        Args:
            file_data (bytes): PowerPoint file binary content (.ppt or .pptx).
            file_name (str): Presentation filename for display and download.
            size_mb (float): File size in megabytes.
            file_id (str or None): Drive file ID for browser viewing.

        Returns:
            ft.Column: Placeholder widget with PowerPoint icon, metadata, and actions.

        Algorithm:
            Similar to _create_word_preview but with:
            - ORANGE SLIDESHOW icon
            - Title: "Presentation Document"
            - Download button: "Download Presentation"
            - ORANGE Open button color

        See Also:
            - :meth:`_create_word_preview`: Similar structure

        Notes:
            - Supports both .ppt and .pptx
            - ORANGE icon (standard PowerPoint color)
            - No inline slide viewer
        """
        return ft.Column([
            ft.Icon(ft.Icons.SLIDESHOW, size=100, color=ft.Colors.ORANGE),
            ft.Text("Presentation Document", size=20, weight=ft.FontWeight.BOLD),
            ft.Text(f"Size: {size_mb:.2f} MB", size=14),
            ft.Text("Presentation preview is not available in-app", size=12, italic=True, color=ft.Colors.GREY_600),
            ft.Container(height=20),
            ft.Row([
                ft.ElevatedButton(
                    "Download Presentation",
                    icon=ft.Icons.DOWNLOAD,
                    on_click=lambda e: self._download_file(file_data, file_name)
                ),
                ft.ElevatedButton(
                    "Open in Browser",
                    icon=ft.Icons.OPEN_IN_NEW,
                    on_click=lambda e: self._open_in_browser(file_id),
                    bgcolor=ft.Colors.ORANGE
                ) if file_id else ft.Container()
            ], spacing=10)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
    
    def _create_default_preview(self, file_data, file_name, mime_type, size_mb, file_id):
        """Create generic file preview for unsupported or unknown file types.

        Shows format-appropriate icon based on file extension with download
        and browser options. Fallback for all unhandled file types.

        Args:
            file_data (bytes): File binary content for download.
            file_name (str): Filename for display, extension detection, and download.
            mime_type (str or None): MIME type for display. May be None or "Unknown".
            size_mb (float): File size in megabytes.
            file_id (str or None): Drive file ID for browser viewing.

        Returns:
            ft.Column: Generic placeholder with appropriate icon and actions.

        Algorithm:
            1. **Extract Extension**:
               a. Split filename by '.'
               b. Get last segment: file_name.split('.')[-1]
               c. Convert to lowercase
               d. Store in ext variable
               e. If no '.', ext = ''
            
            2. **Map Extension to Icon**:
               a. Define icon_map dictionary:
                  - Archives: 'zip', 'rar', '7z' → (FOLDER_ZIP, PURPLE)
                  - Video: 'mp4', 'avi', 'mov' → (VIDEO_FILE, RED)
                  - Audio: 'mp3', 'wav' → (AUDIO_FILE, BLUE)
                  - Data: 'json' → (DATA_OBJECT, GREEN)
                  - Code: 'xml' → (CODE, ORANGE)
                  - Database: 'sql' → (STORAGE, BLUE)
               b. Lookup ext in icon_map
               c. Get (icon, color) tuple
               d. Default: (INSERT_DRIVE_FILE, GREY) if not found
            
            3. **Build Info Display**:
               a. Icon with determined icon and color (size 100)
               b. Title: "File Preview Not Available" (size 20, bold)
               c. Type display: f"Type: {mime_type or 'Unknown'}" (size 14, grey)
               d. Size display: f"Size: {size_mb:.2f} MB" (size 14, grey)
            
            4. **Create Action Buttons**:
               a. Download button: "Download File" → _download_file()
               b. Open button (if file_id): "Open in Browser" (BLUE) → _open_in_browser()
            
            5. **Layout and Return**:
               a. Vertical Column layout
               b. Centered alignment
               c. 10px spacing

        Interactions:
            - **str.split()**: Extension extraction
            - **_download_file()**: Download handler
            - **_open_in_browser()**: Browser opener

        Example:
            >>> # ZIP file
            >>> widget = preview_service._create_default_preview(
            ...     zip_data,
            ...     'archive.zip',
            ...     'application/zip',
            ...     5.0,
            ...     None
            ... )
            >>> # Shows PURPLE folder_zip icon
            >>> 
            >>> # Unknown file
            >>> widget = preview_service._create_default_preview(
            ...     data,
            ...     'data.custom',
            ...     'application/octet-stream',
            ...     1.0,
            ...     'drive_id'
            ... )
            >>> # Shows generic grey file icon

        See Also:
            - :meth:`_render_preview`: Calls this for unknown types
            - :meth:`_download_file`: Download handler

        Notes:
            - Fallback for all unsupported types
            - Extension-based icon selection
            - Icon colors match common conventions
            - Supports archives, media, code, data files
            - Generic file icon for truly unknown types
            - Always shows file type and size
            - Download available for all types
        """
        ext = file_name.split('.')[-1].lower() if '.' in file_name else ''
        
        icon_map = {
            'zip': (ft.Icons.FOLDER_ZIP, ft.Colors.PURPLE),
            'rar': (ft.Icons.FOLDER_ZIP, ft.Colors.PURPLE),
            '7z': (ft.Icons.FOLDER_ZIP, ft.Colors.PURPLE),
            'mp4': (ft.Icons.VIDEO_FILE, ft.Colors.RED),
            'avi': (ft.Icons.VIDEO_FILE, ft.Colors.RED),
            'mov': (ft.Icons.VIDEO_FILE, ft.Colors.RED),
            'mp3': (ft.Icons.AUDIO_FILE, ft.Colors.BLUE),
            'wav': (ft.Icons.AUDIO_FILE, ft.Colors.BLUE),
            'json': (ft.Icons.DATA_OBJECT, ft.Colors.GREEN),
            'xml': (ft.Icons.CODE, ft.Colors.ORANGE),
            'sql': (ft.Icons.STORAGE, ft.Colors.BLUE),
        }
        
        icon, color = icon_map.get(ext, (ft.Icons.INSERT_DRIVE_FILE, ft.Colors.GREY))
        
        return ft.Column([
            ft.Icon(icon, size=100, color=color),
            ft.Text("File Preview Not Available", size=20, weight=ft.FontWeight.BOLD),
            ft.Text(f"Type: {mime_type or 'Unknown'}", size=14, color=ft.Colors.GREY_700),
            ft.Text(f"Size: {size_mb:.2f} MB", size=14, color=ft.Colors.GREY_700),
            ft.Container(height=20),
            ft.Row([
                ft.ElevatedButton(
                    "Download File",
                    icon=ft.Icons.DOWNLOAD,
                    on_click=lambda e: self._download_file(file_data, file_name)
                ),
                ft.ElevatedButton(
                    "Open in Browser",
                    icon=ft.Icons.OPEN_IN_NEW,
                    on_click=lambda e: self._open_in_browser(file_id),
                    bgcolor=ft.Colors.BLUE
                ) if file_id else ft.Container()
            ], spacing=10)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
    
    def _create_error_view(self, error_message, file_id=None):
        """Create error message widget for failed file loading.

        Displays user-friendly error state when file cannot be loaded.
        Provides fallback browser option if Drive file.

        Args:
            error_message (str): Error description to display. Should be
                user-friendly and concise. Example: "Error loading file: File not found"
            file_id (str, optional): Drive file ID for fallback browser viewing.
                If provided, shows "Open in Browser" button. Defaults to None.

        Returns:
            ft.Column: Error widget with icon, message, and optional action.

        Algorithm:
            1. **Build Error Display**:
               a. RED ERROR icon (size 48)
               b. Error message text (RED, center-aligned)
            
            2. **Add Fallback Action** (if file_id):
               a. Add 20px spacing Container
               b. Add "Open in Browser" button:
                  i. Icon: OPEN_IN_NEW
                  ii. on_click: lambda e: _open_in_browser(file_id)
            
            3. **Layout and Return**:
               a. Vertical Column layout
               b. Centered alignment

        Interactions:
            - **_open_in_browser()**: Fallback browser viewing

        Example:
            >>> # Drive file error with fallback
            >>> widget = preview_service._create_error_view(
            ...     "Error loading file: Permission denied",
            ...     file_id='drive_id'
            ... )
            >>> # Shows error with browser button
            >>> 
            >>> # Local file error (no fallback)
            >>> widget = preview_service._create_error_view(
            ...     "Error loading file: File not found"
            ... )
            >>> # Shows error only

        See Also:
            - :meth:`_load_from_drive`: Uses this on errors
            - :meth:`_load_from_path`: Uses this on errors

        Notes:
            - User-friendly error display
            - RED icon and text (clear error indication)
            - Browser fallback for Drive files only
            - No fallback for local file errors
            - Error message should be concise
        """
        return ft.Column([
            ft.Icon(ft.Icons.ERROR, size=48, color=ft.Colors.RED),
            ft.Text(error_message, color=ft.Colors.RED, text_align=ft.TextAlign.CENTER),
            ft.Container(height=20),
            ft.ElevatedButton(
                "Open in Browser",
                icon=ft.Icons.OPEN_IN_NEW,
                on_click=lambda e: self._open_in_browser(file_id)
            ) if file_id else ft.Container()
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    def _download_file(self, file_data, file_name):
        """Save file content to Downloads folder with duplicate handling.

        Writes binary file data to user's Downloads directory. Handles filename
        conflicts by appending (1), (2), etc. Shows success/failure feedback.

        Args:
            file_data (bytes): Complete file content to save.
            file_name (str): Target filename including extension.

        Returns:
            None: Saves file and shows snackbar as side effects.

        Algorithm:
            1. **Try File Save**:
               a. Enter try block for error handling
               b. Import Path from pathlib
            
            2. **Build Download Path**:
               a. Get home directory: Path.home()
               b. Append Downloads subfolder
               c. Append file_name
               d. Store in downloads_path
            
            3. **Handle Name Conflicts**:
               a. Set counter = 1
               b. Store original_path = downloads_path
               c. While downloads_path.exists():
                  i. Split into stem and suffix (name and extension)
                  ii. Build new path: "{name} ({counter}){ext}"
                  iii. Increment counter
                  iv. Repeat until unique path found
            
            4. **Write File**:
               a. Open downloads_path in binary write mode ('wb')
               b. Use context manager for automatic closing
               c. Write file_data: f.write(file_data)
            
            5. **Show Success**:
               a. Format message: f"✓ Downloaded to: {downloads_path.name}"
               b. Call _show_snackbar(message, GREEN)
            
            6. **Handle Errors**:
               a. Catch any Exception during save
               b. Format error: f"✗ Download failed: {str(e)}"
               c. Call _show_snackbar(error, RED)

        Interactions:
            - **pathlib.Path**: File path operations
            - **File I/O**: Writes file to disk
            - **_show_snackbar()**: User feedback

        Example:
            >>> # Download file
            >>> file_data = b'content...'
            >>> preview_service._download_file(file_data, 'document.pdf')
            >>> # Saves to ~/Downloads/document.pdf
            >>> # Shows "✓ Downloaded to: document.pdf"
            >>> 
            >>> # Duplicate filename
            >>> preview_service._download_file(file_data, 'document.pdf')
            >>> # Saves to ~/Downloads/document (1).pdf
            >>> # Shows "✓ Downloaded to: document (1).pdf"

        See Also:
            - :meth:`_create_pdf_preview`: Provides download button
            - :meth:`_show_snackbar`: Feedback display

        Notes:
            - Saves to Downloads folder only
            - Auto-handles filename conflicts
            - Counter appended in format: "file (1).ext"
            - Green snackbar for success
            - Red snackbar for errors
            - Entire file written at once (not chunked)
        """
        try:
            from pathlib import Path
            
            downloads_path = Path.home() / "Downloads" / file_name
            
            counter = 1
            original_path = downloads_path
            while downloads_path.exists():
                name, ext = original_path.stem, original_path.suffix
                downloads_path = original_path.parent / f"{name} ({counter}){ext}"
                counter += 1
            
            with open(downloads_path, 'wb') as f:
                f.write(file_data)
            
            show_snackbar(self.page, f"✓ Downloaded to: {downloads_path.name}", ft.Colors.GREEN)
        except Exception as e:
            show_snackbar(self.page, f"✗ Download failed: {str(e)}", ft.Colors.RED)
    
    def _open_in_browser(self, file_id):
        """Open file in system default browser via Google Drive web interface.

        Launches browser to Drive file viewer. Only works for Drive-hosted files.

        Args:
            file_id (str or None): Google Drive file ID. If None, no action taken.

        Returns:
            None: Opens browser as side effect.

        Algorithm:
            1. **Check File ID**:
               a. If file_id is None, return early
            
            2. **Open Browser**:
               a. Import webbrowser module
               b. Build URL: f"https://drive.google.com/file/d/{file_id}/view"
               c. Call webbrowser.open(url)
               d. Opens in default browser

        Interactions:
            - **webbrowser.open()**: Browser launcher

        Example:
            >>> # Open Drive file
            >>> preview_service._open_in_browser('drive_file_id')
            >>> # Browser opens to Drive viewer
            >>> 
            >>> # No file_id (no action)
            >>> preview_service._open_in_browser(None)
            >>> # Nothing happens

        See Also:
            - :meth:`_create_pdf_preview`: Provides browser button
            - :mod:`webbrowser`: Browser control

        Notes:
            - Only for Drive-hosted files
            - Requires valid file_id
            - Opens Drive web viewer
            - User must have view permissions
            - No action if file_id is None
        """
        if file_id:
            import webbrowser
            webbrowser.open(f"https://drive.google.com/file/d/{file_id}/view")
    
    
    def close_preview(self):
        """Close currently displayed preview overlay.

        Removes preview overlay from page and cleans up references.
        Safe to call even if no preview is active.

        Returns:
            None: Removes overlay and updates page as side effects.

        Algorithm:
            1. **Check Overlay Exists**:
               a. If current_overlay is None, return early
               b. If current_overlay not in page.overlay, return early
            
            2. **Remove Overlay**:
               a. Call page.overlay.remove(current_overlay)
               b. Removes from overlay list
            
            3. **Clear Reference**:
               a. Set current_overlay = None
               b. Prevents dangling reference
            
            4. **Update Page**:
               a. Call page.update()
               b. Renders removal

        Interactions:
            - **page.overlay**: Overlay list management
            - **page.update()**: UI refresh

        Example:
            >>> # Close active preview
            >>> preview_service.show_preview(file_path='file.txt')
            >>> # Preview displayed
            >>> preview_service.close_preview()
            >>> # Preview removed
            >>> 
            >>> # Safe to call when no preview
            >>> preview_service.close_preview()
            >>> # No error, no action

        See Also:
            - :meth:`show_preview`: Opens preview (registers close button)

        Notes:
            - Safe to call multiple times
            - No error if no active preview
            - Clears overlay reference
            - User can also close via close button in overlay
            - Removes entire overlay from page
        """
        if self.current_overlay and self.current_overlay in self.page.overlay:
            self.page.overlay.remove(self.current_overlay)
            self.current_overlay = None
            self.page.update()