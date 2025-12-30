"""File Manager Module.

This module handles file and folder operations within the dashboard,
managing the display and interaction logic for filesystem items.

Classes:
    FileManager: Manages file item creation, menus, and dialogs.

See Also:
    :class:`~src.ui.dashboard.Dashboard`: Connects FileManager to the UI.
    :class:`~src.services.drive_service.DriveService`: Performs the backend operations.
"""

import flet as ft
from utils.common import format_file_size, create_icon_button, open_drive_file


class FileManager:
    """Dashboard file and folder operations manager with UI component generation.

    FileManager handles all file and folder-related UI components and user interactions
    within the Dashboard. It creates visual representations (list items) for files and
    folders, manages context menus with actions (preview, rename, delete, info), and
    orchestrates modal dialogs for operations like creating folders, renaming items,
    and confirming deletions.
    
    This class acts as a bridge between the Dashboard UI and the DriveService backend,
    translating user interactions into Drive API operations and updating the UI with
    results. It implements a consistent interaction pattern across all file operations
    with visual feedback, confirmation dialogs, and error handling.

    Purpose:
        - Generate UI components for files and folders
        - Manage context menus with file operations
        - Handle file preview initialization
        - Orchestrate rename and delete dialogs
        - Create new folder dialog and upload interface
        - Provide file information display
        - Navigate folder hierarchy
        - Coordinate between UI and Drive service

    Attributes:
        dash (Dashboard): Reference to parent Dashboard instance. Provides access
            to page, drive service, current folder state, and UI refresh methods.
            Used for all Dashboard state modifications and updates.
        file_preview (FilePreviewService or None): Service for displaying file
            previews in modal overlays. Handles images, text, PDFs, and Office
            documents. None if service import fails (graceful degradation).

    Interactions:
        - **Dashboard**: Parent container managing overall state
        - **DriveService**: Backend for Drive API operations (via dash.drive)
        - **FilePreviewService**: File preview modal display
        - **ft.Container**: File/folder list item containers
        - **ft.PopupMenuButton**: Context menu implementation
        - **ft.FilePicker**: System file selection dialog
        - **utils.common**: Utility functions (format_file_size, create_icon_button, etc.)

    Algorithm (High-Level Workflow):
        **Phase 1: Initialization**
            1. Store Dashboard reference
            2. Import FilePreviewService (graceful failure if unavailable)
            3. Initialize preview service with page and drive
            4. Ready to create file/folder components
        
        **Phase 2: UI Component Creation**
            1. Dashboard requests file/folder items
            2. FileManager creates styled containers:
               a. Folders: Icon, name, subfolder count, menu
               b. Files: Icon, name, size, preview button, menu
            3. Attach click handlers and context menus
            4. Return components to Dashboard for display
        
        **Phase 3: User Interaction Handling**
            1. User clicks item:
               a. Folders → navigate to folder contents
               b. Files → open preview overlay
            2. User opens context menu:
               a. Preview (files only) → show preview
               b. Info → display file metadata dialog
               c. Rename → show rename input dialog
               d. Delete → show confirmation dialog
        
        **Phase 4: Operation Execution**
            1. User confirms action in dialog
            2. Call appropriate DriveService method
            3. Update Dashboard UI (refresh or optimistic update)
            4. Invalidate Drive cache if needed
            5. Close dialog and show feedback
        
        **Phase 5: File Operations**
            1. Create Folder: Input → API call → Optimistic UI update
            2. Upload File: File picker → Upload → Refresh
            3. Rename: Input → API call → Refresh
            4. Delete: Confirm → API call → Refresh

    Example:
        >>> # Initialize in Dashboard
        >>> from ui.dashboard_modules.file_manager import FileManager
        >>> file_manager = FileManager(dashboard)
        >>> 
        >>> # Create folder item for display
        >>> folder_metadata = {
        ...     'id': 'folder_123',
        ...     'name': 'Documents',
        ...     'mimeType': 'application/vnd.google-apps.folder'
        ... }
        >>> folder_item = file_manager.create_folder_item(
        ...     folder_metadata,
        ...     subfolder_count=5
        ... )
        >>> dashboard.folder_list.controls.append(folder_item)
        >>> 
        >>> # Create file item
        >>> file_metadata = {
        ...     'id': 'file_456',
        ...     'name': 'report.pdf',
        ...     'mimeType': 'application/pdf',
        ...     'size': '2048576'
        ... }
        >>> file_item = file_manager.create_file_item(file_metadata)
        >>> 
        >>> # User interactions handled automatically
        >>> # Click folder → navigates to folder
        >>> # Click file → opens preview
        >>> # Right-click/menu → shows context actions
        >>> 
        >>> # Programmatic operations
        >>> file_manager.create_new_folder_dialog()  # Shows dialog
        >>> file_manager.select_file_to_upload()     # Opens picker

    See Also:
        - :class:`~ui.dashboard.Dashboard`: Parent container
        - :class:`~services.drive_service.DriveService`: Backend operations
        - :class:`~services.file_preview_service.FilePreviewService`: Preview display
        - :func:`~utils.common.format_file_size`: Size formatting
        - :func:`~utils.common.create_icon_button`: Icon button helper

    Notes:
        - All file operations refresh Dashboard after completion
        - Context menus dynamically generated based on item type
        - Preview available only for files (not folders)
        - Dialogs use overlay system (modal, blocks interaction)
        - Optimistic UI updates for folder creation
        - Cache invalidation ensures data consistency
        - Graceful degradation if preview service unavailable
        - Truncates long names (>40 chars) with ellipsis
        - Shared drive flag affects menu options

    Design Patterns:
        - **Facade**: Simplifies complex Drive operations for Dashboard
        - **Factory**: Creates UI components from metadata
        - **Observer**: UI updates in response to Drive operations
        - **Template Method**: Consistent dialog structure

    UI Components Created:
        - Folder list items (icon, name, count, menu)
        - File list items (icon, name, size, actions, menu)
        - Context menus (preview, info, rename, delete)
        - Rename dialog (input field, confirm/cancel)
        - Delete confirmation dialog (warning, confirm/cancel)
        - File info dialog (metadata display, actions)
        - Create folder dialog (name input, create/cancel)
        - File upload picker (system dialog)

    References:
        - Material Design Lists: https://m3.material.io/components/lists
        - Flet Controls: https://flet.dev/docs/controls
        - Google Drive API: https://developers.google.com/drive/api/v3/reference
    """

    def __init__(self, dashboard):
        """Initialize FileManager with Dashboard reference and preview service.

        Sets up file management capabilities by storing Dashboard reference and
        initializing FilePreviewService for file preview functionality. Handles
        import failure gracefully for preview service.

        Args:
            dashboard (Dashboard): Parent Dashboard instance providing access to
                page, Drive service, current folder state, and UI update methods.
                Must have page, drive, and folder-related attributes initialized.

        Algorithm:
            1. **Store Dashboard Reference**:
               a. Assign dashboard parameter to self.dash
               b. Used for all Dashboard state access and updates
            
            2. **Initialize Preview Service**:
               a. Enter try block for graceful failure handling
               b. Import FilePreviewService from services module
               c. Instantiate with dashboard.page and dashboard.drive
               d. Store in self.file_preview
            
            3. **Handle Import Failure**:
               a. Catch ImportError if service unavailable
               b. Set self.file_preview = None
               c. Preview functionality disabled but other features work
               d. No error raised (graceful degradation)

        Interactions:
            - **Dashboard**: Stores reference for state access
            - **FilePreviewService**: Initializes if available

        Example:
            >>> # Standard initialization
            >>> dashboard = Dashboard(page, auth_service)
            >>> file_manager = FileManager(dashboard)
            >>> print(file_manager.file_preview)
            <FilePreviewService instance>
            >>> 
            >>> # Preview service unavailable
            >>> # (service not installed or import error)
            >>> file_manager = FileManager(dashboard)
            >>> print(file_manager.file_preview)
            None
            >>> # Manager still functional, preview disabled

        See Also:
            - :class:`~ui.dashboard.Dashboard`: Parent container
            - :class:`~services.file_preview_service.FilePreviewService`: Preview service

        Notes:
            - Dashboard must be initialized before FileManager
            - Preview service optional (graceful degradation)
            - No exceptions raised on initialization
            - file_preview checked before use in other methods
        """
        self.dash = dashboard
        
        try:
            from services.file_preview_service import FilePreviewService
            self.file_preview = FilePreviewService(dashboard.page, dashboard.drive)
        except ImportError:
            self.file_preview = None

    def show_menu(self, item, is_folder=False, is_shared_drive=False):
        """Generate context menu items for file or folder operations.

        Creates list of PopupMenuItem objects representing available actions
        for the given file or folder. Menu content varies based on item type
        and preview service availability.

        Args:
            item (dict): File or folder metadata dictionary containing at minimum
                'id' and 'name' keys. May include 'mimeType', 'size', etc.
            is_folder (bool, optional): Whether item is a folder. Affects menu
                options (folders cannot be previewed). Defaults to False.
            is_shared_drive (bool, optional): Whether item is shared drive root.
                May affect permissions and available operations. Defaults to False.

        Returns:
            list[ft.PopupMenuItem]: List of menu action items. Each item has text
                label and on_click handler. List may include:
                - "Preview" (files only, if preview service available)
                - "Info" (always)
                - "Rename" (always)
                - "Delete" (always)
                None items filtered out before return.

        Algorithm:
            1. **Define Action Handlers** (local closures):
               a. on_preview(e):
                  i. Check if not folder
                  ii. Call self.preview_file(item)
               b. on_rename(e):
                  i. Call self._rename_file_dialog(item)
               c. on_delete(e):
                  i. Call self._delete_file_dialog(item)
               d. on_info(e):
                  i. Call self.show_file_info(item)
            
            2. **Build Menu Items List**:
               a. Create list with conditional items:
                  i. Preview: if file_preview exists AND not folder
                  ii. Info: always included
                  iii. Rename: always included
                  iv. Delete: always included
               b. Use ternary: item if condition else None
            
            3. **Filter None Values**:
               a. List comprehension: [item for item if item is not None]
               b. Removes conditional items that weren't included
            
            4. **Return Filtered List**:
               a. Return list of valid PopupMenuItem objects

        Interactions:
            - **preview_file()**: Opens preview overlay
            - **_rename_file_dialog()**: Shows rename input
            - **_delete_file_dialog()**: Shows delete confirmation
            - **show_file_info()**: Displays file metadata
            - **ft.PopupMenuItem**: Menu item controls

        Example:
            >>> # File menu (preview available)
            >>> file_meta = {'id': '123', 'name': 'doc.pdf', 'mimeType': 'application/pdf'}
            >>> menu = file_manager.show_menu(file_meta, is_folder=False)
            >>> print([item.text for item in menu])
            ['Preview', 'Info', 'Rename', 'Delete']
            >>> 
            >>> # Folder menu (no preview)
            >>> folder_meta = {'id': '456', 'name': 'Docs', 'mimeType': 'application/vnd.google-apps.folder'}
            >>> menu = file_manager.show_menu(folder_meta, is_folder=True)
            >>> print([item.text for item in menu])
            ['Info', 'Rename', 'Delete']
            >>> 
            >>> # Without preview service
            >>> file_manager.file_preview = None
            >>> menu = file_manager.show_menu(file_meta, is_folder=False)
            >>> print([item.text for item in menu])
            ['Info', 'Rename', 'Delete']

        See Also:
            - :meth:`preview_file`: Preview handler
            - :meth:`_rename_file_dialog`: Rename dialog
            - :meth:`_delete_file_dialog`: Delete confirmation
            - :meth:`show_file_info`: Info display
            - :class:`ft.PopupMenuItem`: Flet menu item

        Notes:
            - Menu dynamically generated per item
            - Preview only for files with service available
            - All items get info, rename, delete options
            - Closures capture item in handler scope
            - Filtered list contains no None values
            - is_shared_drive currently unused but available
        """

        def on_rename(e):
            self._rename_file_dialog(item)

        def on_delete(e):
            self._delete_file_dialog(item)

        def on_info(e):
            self.show_file_info(item)
        
        menu_items = [
            ft.PopupMenuItem(text="Info", icon=ft.Icons.INFO, on_click=on_info),
            ft.PopupMenuItem(text="Rename", icon=ft.Icons.EDIT, on_click=on_rename),
            ft.PopupMenuItem(text="Delete", icon=ft.Icons.DELETE, on_click=on_delete),
        ]

        return [item for item in menu_items if item is not None]

    def create_folder_item(self, folder, subfolder_count, is_shared_drive=False):
        """Create visual folder list item with icon, name, count, and menu.

        Generates styled Container representing folder in file list. Includes
        folder icon, display name (truncated if long), subfolder count, and
        context menu. Click opens folder contents.

        Args:
            folder (dict): Folder metadata dictionary. Must contain:
                - 'name' (str): Folder display name
                - 'id' (str): Folder Drive ID
                May contain additional metadata keys.
            subfolder_count (int): Number of subfolders within this folder.
                Displayed as "{count} folders" text. May be 0.
            is_shared_drive (bool, optional): Whether folder is shared drive root.
                Passed to open_folder and show_menu. Defaults to False.

        Returns:
            ft.Container: Styled clickable folder list item. Contains Row with:
                - Folder icon (24px)
                - Column with name and subfolder count
                - PopupMenuButton with context menu
                Has bottom border, padding, and click handler.

        Algorithm:
            1. **Extract and Format Name**:
               a. Get folder name: folder.get("name", "Untitled")
               b. If length > 40 characters:
                  i. Truncate to 37 chars
                  ii. Append "..." (ellipsis)
                  iii. Store in display_name
               c. Else: display_name = folder_name as-is
            
            2. **Generate Context Menu**:
               a. Call self.show_menu(folder, is_folder=True, is_shared_drive)
               b. Returns list of PopupMenuItem objects
               c. Store in menu_items
            
            3. **Build UI Structure**:
               a. Create ft.Row with components:
                  i. ft.Icon(FOLDER, size=24)
                  ii. ft.Column(expand=True):
                      - ft.Text(display_name, size=14)
                      - ft.Text(f"{subfolder_count} folders", size=12, grey)
                  iii. ft.PopupMenuButton(items=menu_items)
            
            4. **Wrap in Container**:
               a. Set content to Row
               b. Set padding: 10px
               c. Set border: bottom only, 1px grey
               d. Register on_click handler:
                  i. Lambda captures folder reference
                  ii. Calls self.open_folder(folder, is_shared_drive)
            
            5. **Return Container**:
               a. Return styled, clickable folder item

        Interactions:
            - **show_menu()**: Generates context menu
            - **open_folder()**: Click handler
            - **ft.Container, ft.Row, ft.Column**: Layout
            - **ft.Icon, ft.Text**: Visual elements
            - **ft.PopupMenuButton**: Menu display

        Example:
            >>> # Create folder item
            >>> folder = {
            ...     'id': 'folder_abc123',
            ...     'name': 'My Documents',
            ...     'mimeType': 'application/vnd.google-apps.folder'
            ... }
            >>> item = file_manager.create_folder_item(folder, subfolder_count=5)
            >>> dashboard.folder_list.controls.append(item)
            >>> 
            >>> # Long name truncation
            >>> long_folder = {
            ...     'id': 'folder_xyz',
            ...     'name': 'This is a very long folder name that exceeds forty characters'
            ... }
            >>> item = file_manager.create_folder_item(long_folder, 0)
            >>> # Display shows: "This is a very long folder name th..."
            >>> 
            >>> # Shared drive folder
            >>> shared = {'id': 'shared_123', 'name': 'Team Drive'}
            >>> item = file_manager.create_folder_item(
            ...     shared,
            ...     subfolder_count=10,
            ...     is_shared_drive=True
            ... )

        See Also:
            - :meth:`show_menu`: Context menu generation
            - :meth:`open_folder`: Click handler
            - :meth:`create_file_item`: Similar for files

        Notes:
            - Name truncated at 40 characters (37 + "...")
            - Subfolder count informational only
            - Click opens folder contents (navigates)
            - Context menu via three-dot button
            - Bottom border separates list items
            - Icon always folder icon (not dynamic)
            - is_shared_drive affects navigation behavior
        """
        folder_name = folder.get("name", "Untitled")
        display_name = folder_name if len(folder_name) < 40 else folder_name[:37] + "..."
        
        menu_items = self.show_menu(folder, is_folder=True, is_shared_drive=is_shared_drive)

        return ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.FOLDER, size=24),
                    ft.Column([
                        ft.Text(display_name, size=14),
                        ft.Text(f"{subfolder_count} folders", size=12, color=ft.Colors.GREY_600),
                    ], expand=True),
                    ft.PopupMenuButton(items=menu_items),
                ]),
                padding=8,
                ink=True,
                on_click=lambda e, f=folder: self.open_folder(f, is_shared_drive),
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=8,
                margin=ft.margin.only(bottom=10)
            )
        
    
    def create_file_item(self, file):
        """Create visual file list item with icon, name, size, and actions.

        Generates styled Container representing file in list. Includes appropriate
        icon, file name, size display, preview button (if available), and context
        menu. Click opens file preview.

        Args:
            file (dict): File metadata dictionary. Should contain:
                - 'id' (str): File Drive ID
                - 'name' (str): File display name
                - 'mimeType' (str): File MIME type
                - 'size' (str or int, optional): File size in bytes
                Additional metadata keys may be present.

        Returns:
            ft.Container: Styled clickable file list item. Contains Row with:
                - File/folder icon (24px)
                - Column with name and size
                - Preview button (if file and service available)
                - PopupMenuButton with context menu
                Has bottom border, padding, and click handler.

        Algorithm:
            1. **Determine Item Type**:
               a. Check mimeType: file.get("mimeType")
               b. Set is_folder = (mimeType == "application/vnd.google-apps.folder")
               c. Handles rare case of folder in file list
            
            2. **Select Icon and Size**:
               a. If is_folder:
                  i. icon = ft.Icons.FOLDER
                  ii. size_str = "Folder"
               b. Else (regular file):
                  i. icon = ft.Icons.INSERT_DRIVE_FILE
                  ii. size_str = format_file_size(file.get("size"))
                  iii. Formats bytes to human-readable (KB, MB, etc.)
            
            3. **Generate Context Menu**:
               a. Call self.show_menu(file, is_folder=is_folder)
               b. Returns list of PopupMenuItem objects
            
            4. **Build Action Buttons**:
               a. Initialize empty list: action_buttons
               b. If not folder AND preview service exists:
                  i. Create preview icon button:
                     - Icon: VISIBILITY
                     - Tooltip: "Preview"
                     - on_click: lambda captures file, calls preview_file
                  ii. Append to action_buttons
               c. Always append PopupMenuButton(items=menu_items)
            
            5. **Build UI Structure**:
               a. Create ft.Row with:
                  i. ft.Icon(icon, size=24)
                  ii. ft.Column(expand=True):
                      - ft.Text(file.get("name", "Untitled"), size=14)
                      - ft.Text(size_str, size=12, grey)
                  iii. *action_buttons (unpacked list)
            
            6. **Wrap in Container**:
               a. Set content to Row
               b. Set padding: 10px
               c. Set border: bottom only, 1px light grey
               d. Register on_click handler:
                  i. If folder: lambda calls handle_file_click(file)
                  ii. If file: lambda calls preview_file(file)
            
            7. **Return Container**:
               a. Return styled, clickable file item

        Interactions:
            - **show_menu()**: Context menu generation
            - **preview_file()**: Preview handler
            - **handle_file_click()**: Folder navigation
            - **format_file_size()**: Size formatting (utils.common)
            - **create_icon_button()**: Button helper (utils.common)
            - **ft.Container, ft.Row, ft.Column**: Layout

        Example:
            >>> # Regular file
            >>> file = {
            ...     'id': 'file_123',
            ...     'name': 'report.pdf',
            ...     'mimeType': 'application/pdf',
            ...     'size': '2048576'  # 2MB
            ... }
            >>> item = file_manager.create_file_item(file)
            >>> # Shows: PDF icon, "report.pdf", "2.00 MB", preview + menu
            >>> 
            >>> # Image file
            >>> image = {
            ...     'id': 'img_456',
            ...     'name': 'photo.jpg',
            ...     'mimeType': 'image/jpeg',
            ...     'size': '1048576'  # 1MB
            ... }
            >>> item = file_manager.create_file_item(image)
            >>> # Click opens image preview
            >>> 
            >>> # Folder in file list (edge case)
            >>> folder = {
            ...     'id': 'folder_789',
            ...     'name': 'Subfolder',
            ...     'mimeType': 'application/vnd.google-apps.folder'
            ... }
            >>> item = file_manager.create_file_item(folder)
            >>> # Shows folder icon, "Folder", no preview button
            >>> # Click navigates to folder

        See Also:
            - :meth:`show_menu`: Context menu
            - :meth:`preview_file`: Preview handler
            - :meth:`handle_file_click`: Folder handler
            - :func:`~utils.common.format_file_size`: Size formatter
            - :func:`~utils.common.create_icon_button`: Button helper

        Notes:
            - Handles both files and folders (edge case)
            - Preview button only for files with service
            - Size formatted for readability
            - Generic file icon (not MIME-specific)
            - Click behavior differs: folder → navigate, file → preview
            - Action buttons list allows flexible additions
            - Bottom border lighter than folder items (visual hierarchy)
        """
        is_folder = file.get("mimeType") == "application/vnd.google-apps.folder"
        icon = ft.Icons.FOLDER if is_folder else ft.Icons.INSERT_DRIVE_FILE
        size_str = "Folder" if is_folder else format_file_size(file.get("size"))

        menu_items = self.show_menu(file, is_folder=is_folder)
        action_buttons = []
        if not is_folder and self.file_preview:
            action_buttons.append(
                create_icon_button(ft.Icons.VISIBILITY, "Preview", 
                                  lambda e, f=file: self.preview_file(f))
            )
        action_buttons.append(
            ft.PopupMenuButton(items=menu_items)
        )

        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, size=24),
                ft.Column([
                    ft.Text(file.get("name", "Untitled"), size=14),
                    ft.Text(size_str, size=12, color=ft.Colors.GREY_600),
                ], expand=True),
                *action_buttons
            ]),
            padding=10,
            ink=True,
            on_click=lambda e, f=file: self.handle_file_click(f) if is_folder else self.preview_file(f),
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            margin=ft.margin.only(bottom=10),
        )
    
    def preview_file(self, file):
        """Open file preview overlay for supported file types.

        Initiates FilePreviewService to display file in modal overlay.
        Checks for service availability and ensures item is not a folder
        before attempting preview.

        Args:
            file (dict): File metadata dictionary containing:
                - 'id' (str): File Drive ID for fetching content
                - 'name' (str): File name for display
                - 'mimeType' (str): Used to check if folder
                Additional metadata may be present.

        Returns:
            None: Opens preview overlay as side effect. No return value.

        Algorithm:
            1. **Check Preview Service**:
               a. If self.file_preview is None:
                  i. Service not available
                  ii. Return early (no preview)
            
            2. **Check Item Type**:
               a. Get mimeType: file.get("mimeType")
               b. If mimeType == "application/vnd.google-apps.folder":
                  i. Item is folder (cannot preview)
                  ii. Return early
            
            3. **Open Preview**:
               a. Call file_preview.show_preview() with:
                  i. file_id: file.get("id")
                  ii. file_name: file.get("name", "File")
               b. Service handles:
                  i. File download from Drive
                  ii. Format detection
                  iii. Preview rendering
                  iv. Modal overlay display

        Interactions:
            - **FilePreviewService.show_preview()**: Opens preview
            - **DriveService**: (via preview service) Downloads file

        Example:
            >>> # Preview PDF file
            >>> pdf_file = {
            ...     'id': 'file_abc123',
            ...     'name': 'document.pdf',
            ...     'mimeType': 'application/pdf'
            ... }
            >>> file_manager.preview_file(pdf_file)
            >>> # Modal overlay opens with PDF preview
            >>> 
            >>> # Preview image
            >>> image = {
            ...     'id': 'img_xyz',
            ...     'name': 'photo.jpg',
            ...     'mimeType': 'image/jpeg'
            ... }
            >>> file_manager.preview_file(image)
            >>> # Image displayed inline in overlay
            >>> 
            >>> # Attempt folder preview (no-op)
            >>> folder = {
            ...     'id': 'folder_123',
            ...     'name': 'Documents',
            ...     'mimeType': 'application/vnd.google-apps.folder'
            ... }
            >>> file_manager.preview_file(folder)
            >>> # Nothing happens (returns early)
            >>> 
            >>> # No preview service (no-op)
            >>> file_manager.file_preview = None
            >>> file_manager.preview_file(pdf_file)
            >>> # Nothing happens (returns early)

        See Also:
            - :class:`~services.file_preview_service.FilePreviewService`: Preview service
            - :meth:`create_file_item`: Adds preview button
            - :meth:`show_menu`: Includes preview in menu

        Notes:
            - Checks both service availability and item type
            - Folders cannot be previewed (early return)
            - Service handles all preview logic
            - Modal overlay blocks interaction
            - Supports images, text, PDFs, Office docs
            - No error raised if service unavailable
            - Preview service downloads file from Drive
        """
        if self.file_preview and file.get("mimeType") != "application/vnd.google-apps.folder":
            self.file_preview.show_preview(
                file_id=file.get("id"),
                file_name=file.get("name", "File")
            )
    
    def open_folder(self, folder, is_shared_drive=False):
        """Navigate Dashboard to display folder contents.

        Triggers Dashboard to change current view to specified folder,
        loading and displaying its contents. Updates breadcrumb navigation.

        Args:
            folder (dict): Folder metadata dictionary containing:
                - 'id' (str): Folder Drive ID for content fetching
                - 'name' (str, optional): Folder name for breadcrumb
                Additional metadata may be present.
            is_shared_drive (bool, optional): Whether folder is within shared
                drive. Affects navigation and permissions. Defaults to False.

        Returns:
            None: Updates Dashboard state as side effect.

        Algorithm:
            1. **Extract Folder Info**:
               a. Get folder ID: folder["id"]
               b. Get folder name: folder.get("name", folder["id"])
               c. Use ID as fallback if name missing
            
            2. **Trigger Navigation**:
               a. Call dash.show_folder_contents() with:
                  i. folder_id: extracted ID
                  ii. folder_name: extracted name
                  iii. is_shared_drive: flag parameter
               b. Dashboard handles:
                  i. Fetching folder contents from Drive
                  ii. Updating current_folder_id state
                  iii. Refreshing file list display
                  iv. Updating breadcrumb navigation

        Interactions:
            - **Dashboard.show_folder_contents()**: Navigation method
            - **DriveService**: (via Dashboard) Fetches contents

        Example:
            >>> # Navigate to folder
            >>> folder = {
            ...     'id': 'folder_abc123',
            ...     'name': 'Documents',
            ...     'mimeType': 'application/vnd.google-apps.folder'
            ... }
            >>> file_manager.open_folder(folder)
            >>> # Dashboard displays Documents folder contents
            >>> 
            >>> # Shared drive folder
            >>> shared_folder = {
            ...     'id': 'shared_xyz',
            ...     'name': 'Team Drive'
            ... }
            >>> file_manager.open_folder(shared_folder, is_shared_drive=True)
            >>> 
            >>> # Folder without name (uses ID)
            >>> minimal_folder = {'id': 'folder_123'}
            >>> file_manager.open_folder(minimal_folder)
            >>> # Breadcrumb shows folder_123

        See Also:
            - :meth:`~ui.dashboard.Dashboard.show_folder_contents`: Navigation handler
            - :meth:`handle_file_click`: Routes folder clicks here
            - :meth:`create_folder_item`: Adds click handler

        Notes:
            - Called from folder item click handler
            - Dashboard manages navigation state
            - Breadcrumb updated automatically
            - Contents fetched from Drive API
            - is_shared_drive affects permissions
            - Name fallback to ID if missing
        """
        self.dash.show_folder_contents(folder["id"], folder.get("name", folder["id"]), is_shared_drive)
    
    def handle_file_click(self, file):
        """Route file click to appropriate handler based on type.

        Determines whether clicked item is folder or file and routes to
        appropriate action: navigation for folders, preview for files.

        Args:
            file (dict): File or folder metadata dictionary containing:
                - 'mimeType' (str): Used to determine type
                - 'id' (str): For navigation or preview
                - 'name' (str): For display
                Additional metadata may be present.

        Returns:
            None: Calls appropriate handler as side effect.

        Algorithm:
            1. **Check MIME Type**:
               a. Get mimeType: file.get("mimeType")
               b. Compare to folder MIME type
            
            2. **Route to Handler**:
               a. If mimeType == "application/vnd.google-apps.folder":
                  i. Call dash.show_folder_contents() with:
                     - file["id"]
                     - file["name"]
                  ii. Navigates to folder
               b. Else (regular file):
                  i. Call self.preview_file(file)
                  ii. Opens preview overlay

        Interactions:
            - **Dashboard.show_folder_contents()**: Folder navigation
            - **preview_file()**: File preview

        Example:
            >>> # Click folder
            >>> folder = {
            ...     'id': 'folder_123',
            ...     'name': 'Documents',
            ...     'mimeType': 'application/vnd.google-apps.folder'
            ... }
            >>> file_manager.handle_file_click(folder)
            >>> # Navigates to Documents folder
            >>> 
            >>> # Click file
            >>> file = {
            ...     'id': 'file_456',
            ...     'name': 'report.pdf',
            ...     'mimeType': 'application/pdf'
            ... }
            >>> file_manager.handle_file_click(file)
            >>> # Opens PDF preview

        See Also:
            - :meth:`preview_file`: File preview handler
            - :meth:`~ui.dashboard.Dashboard.show_folder_contents`: Folder handler

        Notes:
            - Simple router based on MIME type
            - Folders navigate, files preview
            - Used in create_file_item click handler
            - MIME type reliable for type detection
        """
        if file.get("mimeType") == "application/vnd.google-apps.folder":
            self.dash.show_folder_contents(file["id"], file["name"])
        else:
            self.preview_file(file)
    
    def show_folder_menu(self, folder, is_shared_drive=False):
        """Open folder navigation (legacy alias for open_folder).

        Alternate entry point for folder navigation. Delegates to open_folder
        for actual implementation. Maintained for backward compatibility.

        Args:
            folder (dict): Folder metadata with 'id' and optional 'name'.
            is_shared_drive (bool, optional): Shared drive flag. Defaults to False.

        Returns:
            None: Delegates to open_folder.

        See Also:
            - :meth:`open_folder`: Actual implementation

        Notes:
            - Legacy method (may be deprecated)
            - Direct alias to open_folder
            - Same behavior and arguments
        """
        self.open_folder(folder, is_shared_drive)
    
    def _rename_file_dialog(self, file):
        """Display modal dialog for renaming file or folder.

        Shows overlay dialog with text input pre-filled with current name.
        User can modify name and confirm or cancel. On confirm, updates
        file via Drive API and refreshes Dashboard.

        Args:
            file (dict): File or folder metadata containing:
                - 'id' (str): Item ID for rename operation
                - 'name' (str): Current name for pre-fill
                Additional metadata may be present but not used.

        Returns:
            None: Shows dialog and handles rename as side effects.

        Algorithm:
            1. **Create Input Field**:
               a. Create ft.TextField with:
                  i. value: file["name"] (pre-filled)
                  ii. autofocus: True (cursor ready)
            
            2. **Define Rename Handler**:
               a. Get new name: name_field.value.strip()
               b. Validate input:
                  i. If empty, return (no-op)
                  ii. If unchanged, return (no-op)
               c. Call API:
                  i. dash.drive.rename_file(file["id"], new_name)
                  ii. Updates file in Drive
               d. Refresh UI:
                  i. dash.refresh_folder_contents()
                  ii. Fetches updated file list
               e. Close dialog:
                  i. Set dialog_container.visible = False
                  ii. Call dash.page.update()
            
            3. **Define Cancel Handler**:
               a. Set dialog_container.visible = False
               b. Call dash.page.update()
               c. No API call (discard changes)
            
            4. **Build Dialog UI**:
               a. Create dialog_container (ft.Container):
                  i. Outer: Semi-transparent black backdrop
                  ii. Inner: White container with:
                      - Title: "Rename" (size 20, bold)
                      - Input field (name_field)
                      - Action Row:
                        - Cancel button (TextButton)
                        - Rename button (ElevatedButton)
                  iii. Centered alignment
                  iv. Width: 400px
            
            5. **Show Dialog**:
               a. Append dialog_container to dash.page.overlay
               b. Call dash.page.update() to render
               c. User interacts with modal

        Interactions:
            - **DriveService.rename_file()**: API rename operation
            - **Dashboard.refresh_folder_contents()**: UI refresh
            - **ft.TextField**: Input control
            - **ft.Container**: Dialog structure
            - **dash.page.overlay**: Modal display

        Example:
            >>> # Rename file
            >>> file = {
            ...     'id': 'file_123',
            ...     'name': 'old_name.pdf',
            ...     'mimeType': 'application/pdf'
            ... }
            >>> file_manager._rename_file_dialog(file)
            >>> # Dialog appears with "old_name.pdf" in input
            >>> # User changes to "new_name.pdf" and clicks Rename
            >>> # → Drive API called: rename_file('file_123', 'new_name.pdf')
            >>> # → Dashboard refreshes to show new name
            >>> # → Dialog closes
            >>> 
            >>> # Cancel rename
            >>> file_manager._rename_file_dialog(file)
            >>> # User clicks Cancel
            >>> # → Dialog closes
            >>> # → No API call, no changes

        See Also:
            - :meth:`show_menu`: Includes rename option
            - :meth:`~services.drive_service.DriveService.rename_file`: API method
            - :meth:`~ui.dashboard.Dashboard.refresh_folder_contents`: Refresh

        Notes:
            - Pre-fills current name for editing
            - Validates non-empty and changed
            - Refreshes Dashboard after rename
            - Modal blocks other interactions
            - Cancel discards changes (no API call)
            - Overlay system for modal behavior
            - Works for both files and folders
        """
        name_field = ft.TextField(value=file["name"], autofocus=True)

        def rename(e):
            new_name = name_field.value.strip()
            if new_name and new_name != file["name"]:
                self.dash.drive.rename_file(file["id"], new_name)
                self.dash.refresh_folder_contents()
            dialog_container.visible = False
            self.dash.page.update()

        def cancel(e):
            dialog_container.visible = False
            self.dash.page.update()

        dialog_container = ft.Container(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Rename", size=20, weight=ft.FontWeight.BOLD),
                    name_field,
                    ft.Row([
                        ft.TextButton("Cancel", on_click=cancel),
                        ft.ElevatedButton("Rename", on_click=rename)
                    ], alignment=ft.MainAxisAlignment.END),
                ], tight=True, spacing=15),
                padding=20,
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                width=400,
            ),
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
        )

        self.dash.page.overlay.append(dialog_container)
        self.dash.page.update()
    
    def _delete_file_dialog(self, file):
        """Display confirmation dialog for file or folder deletion.

        Shows modal dialog with warning message and item name. User must
        confirm deletion before API call. On confirm, deletes from Drive
        and refreshes Dashboard.

        Args:
            file (dict): File or folder metadata containing:
                - 'id' (str): Item ID for deletion
                - 'name' (str): Item name for confirmation message
                Additional metadata may be present.

        Returns:
            None: Shows dialog and handles deletion as side effects.

        Algorithm:
            1. **Define Delete Handler**:
               a. Call API:
                  i. dash.drive.delete_file(file["id"])
                  ii. Permanently deletes from Drive
               b. Refresh UI:
                  i. dash.refresh_folder_contents()
                  ii. Removes item from display
               c. Close dialog:
                  i. Set dialog_container.visible = False
                  ii. Call dash.page.update()
            
            2. **Define Cancel Handler**:
               a. Set dialog_container.visible = False
               b. Call dash.page.update()
               c. No deletion (safe exit)
            
            3. **Build Dialog UI**:
               a. Create dialog_container:
                  i. Outer: Semi-transparent backdrop
                  ii. Inner: White container with:
                      - Title: "Confirm Delete" (size 20, bold)
                      - Warning: "Delete '{name}'?" (file name)
                      - Action Row:
                        - Cancel button (TextButton)
                        - Delete button (ElevatedButton, RED)
                  iii. Centered alignment
                  iv. Width: 400px
            
            4. **Show Dialog**:
               a. Append to dash.page.overlay
               b. Call dash.page.update()
               c. Wait for user interaction

        Interactions:
            - **DriveService.delete_file()**: API delete operation
            - **Dashboard.refresh_folder_contents()**: UI refresh
            - **ft.Container**: Dialog structure
            - **dash.page.overlay**: Modal display

        Example:
            >>> # Delete file with confirmation
            >>> file = {
            ...     'id': 'file_123',
            ...     'name': 'document.pdf',
            ...     'mimeType': 'application/pdf'
            ... }
            >>> file_manager._delete_file_dialog(file)
            >>> # Dialog: "Delete 'document.pdf'?"
            >>> # User clicks Delete (RED button)
            >>> # → Drive API: delete_file('file_123')
            >>> # → Dashboard refreshes
            >>> # → File removed from display
            >>> # → Dialog closes
            >>> 
            >>> # Cancel deletion
            >>> file_manager._delete_file_dialog(file)
            >>> # User clicks Cancel
            >>> # → Dialog closes
            >>> # → No API call, file preserved
            >>> 
            >>> # Delete folder (recursive)
            >>> folder = {
            ...     'id': 'folder_456',
            ...     'name': 'Old Folder'
            ... }
            >>> file_manager._delete_file_dialog(folder)
            >>> # Deletes folder and all contents

        See Also:
            - :meth:`show_menu`: Includes delete option
            - :meth:`~services.drive_service.DriveService.delete_file`: API method
            - :meth:`~ui.dashboard.Dashboard.refresh_folder_contents`: Refresh

        Notes:
            - Confirmation required (safety measure)
            - Shows item name for clarity
            - Delete button RED (danger indicator)
            - Refreshes Dashboard after deletion
            - Permanent deletion (not trash)
            - Modal blocks interactions
            - Works for files and folders
            - Folder deletion is recursive
        """
        def delete(e):
            self.dash.drive.delete_file(file["id"])
            self.dash.refresh_folder_contents()
            dialog_container.visible = False
            self.dash.page.update()

        def cancel(e):
            dialog_container.visible = False
            self.dash.page.update()

        dialog_container = ft.Container(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Confirm Delete", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Delete '{file.get('name', '')}'?"),
                    ft.Row([
                        ft.TextButton("Cancel", on_click=cancel),
                        ft.ElevatedButton("Delete", on_click=delete, bgcolor=ft.Colors.RED)
                    ], alignment=ft.MainAxisAlignment.END),
                ], tight=True, spacing=15),
                padding=20,
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                width=400,
            ),
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
        )

        self.dash.page.overlay.append(dialog_container)
        self.dash.page.update()


    
    def show_file_info(self, file):
        """Display file metadata and actions in modal dialog.

        Shows comprehensive file information including name, type, size,
        and modification date. Provides preview and browser viewing options.
        Fetches full metadata if needed.

        Args:
            file (dict or str): File metadata dictionary or file ID. If dict,
                must contain 'id' key for metadata fetch. If full metadata
                already present, uses directly.

        Returns:
            None: Shows info dialog as side effect.

        Algorithm:
            1. **Fetch Full Metadata** (if needed):
               a. Check if file is dict with 'id' key
               b. If yes:
                  i. Call dash.drive.get_file_info(file["id"])
                  ii. Returns complete metadata
                  iii. Store in info variable
               c. Else:
                  i. Assume file is already full metadata
                  ii. Use directly as info
               d. If info is None:
                  i. Fetch failed
                  ii. Return early (no dialog)
            
            2. **Format Size**:
               a. If info.get('size') exists:
                  i. Call format_file_size(info.get('size'))
                  ii. Converts bytes to readable format
               b. Else:
                  i. size_str = "N/A" (no size available)
            
            3. **Define Close Handler**:
               a. Set dialog_container.visible = False
               b. Call dash.page.update()
            
            4. **Define Preview Handler**:
               a. Call self.preview_file(info)
               b. Set dialog_container.visible = False
               c. Call dash.page.update()
               d. Closes info, opens preview
            
            5. **Create Action Buttons**:
               a. Preview button (if service available):
                  i. Text: "Preview"
                  ii. Icon: VISIBILITY
                  iii. on_click: on_preview
               b. Browser button (always):
                  i. Text: "Open in Browser"
                  ii. Icon: OPEN_IN_NEW
                  iii. on_click: lambda → open_drive_file(info.get('id'))
            
            6. **Build Dialog UI**:
               a. Create dialog_container:
                  i. Title: "File Information" (size 20, bold)
                  ii. Metadata fields:
                      - Name: info.get('name', 'N/A')
                      - Type: info.get('mimeType', 'N/A')
                      - Size: size_str
                      - Modified: info.get('modifiedTime', 'N/A')[:10]
                  iii. Divider separator
                  iv. Action Row: preview + browser buttons
                  v. Close button Row
                  vi. Width: 400px, white background, rounded
            
            7. **Show Dialog**:
               a. Append to dash.page.overlay
               b. Call dash.page.update()

        Interactions:
            - **DriveService.get_file_info()**: Metadata fetch
            - **format_file_size()**: Size formatting
            - **open_drive_file()**: Browser opening
            - **preview_file()**: Preview display
            - **ft.Container**: Dialog structure

        Example:
            >>> # Show info with partial metadata
            >>> file = {'id': 'file_123', 'name': 'document.pdf'}
            >>> file_manager.show_file_info(file)
            >>> # Fetches full metadata from Drive
            >>> # Dialog shows:
            >>> # Name: document.pdf
            >>> # Type: application/pdf
            >>> # Size: 2.5 MB
            >>> # Modified: 2024-01-15
            >>> # [Preview] [Open in Browser] [Close]
            >>> 
            >>> # Show info with full metadata
            >>> full_file = {
            ...     'id': 'file_456',
            ...     'name': 'report.docx',
            ...     'mimeType': 'application/vnd.openxmlformats...',
            ...     'size': '1048576',
            ...     'modifiedTime': '2024-02-20T10:30:00.000Z'
            ... }
            >>> file_manager.show_file_info(full_file)
            >>> # Uses metadata directly (no fetch)
            >>> 
            >>> # Click Preview button
            >>> # → Closes info dialog
            >>> # → Opens preview overlay
            >>> 
            >>> # Click Open in Browser
            >>> # → Opens file in Drive web viewer

        See Also:
            - :meth:`show_menu`: Includes info option
            - :meth:`preview_file`: Preview handler
            - :func:`~utils.common.format_file_size`: Size formatter
            - :func:`~utils.common.open_drive_file`: Browser opener

        Notes:
            - Fetches full metadata if partial provided
            - Shows comprehensive file information
            - Preview option if service available
            - Browser viewing always available
            - Modified date truncated to date only ([:10])
            - Size formatted for readability
            - N/A shown for missing fields
            - Modal blocks interaction
            - Divider separates info from actions
        """
        info = self.dash.drive.get_file_info(file["id"]) if isinstance(file, dict) and "id" in file else file
        if not info:
            return
        
        size_str = format_file_size(info.get('size')) if info.get('size') else "N/A"
        
        def close_dialog(e):
            dialog_container.visible = False
            self.dash.page.update()
        
        def on_preview(e):
            self.preview_file(info)
            dialog_container.visible = False
            self.dash.page.update()
        
        preview_button = (
            ft.ElevatedButton(
                "Preview",
                icon=ft.Icons.VISIBILITY,
                on_click=on_preview
            ) if self.file_preview else ft.Container()
        )
        
        browser_button = ft.ElevatedButton(
            "Open in Browser",
            icon=ft.Icons.OPEN_IN_NEW,
            on_click=lambda e: open_drive_file(info.get('id'))
        )
        
        dialog_container = ft.Container(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("File Information", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Name: {info.get('name', 'N/A')}"),
                    ft.Text(f"Type: {info.get('mimeType', 'N/A')}"),
                    ft.Text(f"Size: {size_str}"),
                    ft.Text(f"Modified: {info.get('modifiedTime', 'N/A')[:10]}"),
                    ft.Divider(),
                    ft.Row([preview_button, browser_button], spacing=10),
                    ft.Row([
                        ft.TextButton("Close", on_click=close_dialog)
                    ], alignment=ft.MainAxisAlignment.END),
                ], tight=True, spacing=10),
                padding=20,
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                width=400,
            ),
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
        )

        self.dash.page.overlay.append(dialog_container)
        self.dash.page.update()

    
    def create_new_folder_dialog(self):
        """Display modal dialog for creating new folder in current directory.

        Shows input dialog for folder name. On creation, calls Drive API,
        performs optimistic UI update (adds folder to list immediately),
        and invalidates cache for consistency.

        Returns:
            None: Shows dialog and handles creation as side effects.

        Algorithm:
            1. **Create Input Controls**:
               a. Create name_field (ft.TextField):
                  i. label: "Folder name"
                  ii. autofocus: True
               b. Create loading_text (ft.Text):
                  i. Initial value: "" (empty)
                  ii. Shows status messages
            
            2. **Define Create Handler**:
               a. Validate input:
                  i. Get folder_name: name_field.value.strip()
                  ii. If empty, return (no-op)
               b. Show loading:
                  i. Set loading_text.value = "Creating folder..."
                  ii. Call dash.page.update()
               c. Call API:
                  i. dash.drive.create_folder(folder_name, parent_id)
                  ii. parent_id = dash.current_folder_id
                  iii. Returns folder metadata dict or None
               d. Handle success:
                  i. If folder is not None:
                     - Remove dialog: dash.page.overlay.pop()
                     - Create UI item:
                       - Call create_folder_item() with:
                         - folder: {'id', 'name', 'mimeType'}
                         - subfolder_count: 0 (new folder empty)
                     - Optimistic update:
                       - insert_position = 1 (after back button)
                       - If space available:
                         - Insert at position 1
                       - Else:
                         - Append to end
                     - Invalidate cache:
                       - dash.drive._invalidate_cache(current_folder_id)
                     - Update UI:
                       - dash.page.update()
               e. Handle failure:
                  i. If folder is None:
                     - Set loading_text.value = "Failed to create folder."
                     - Call dash.page.update()
                     - Dialog remains open
            
            3. **Build Dialog UI**:
               a. Create dialog_container:
                  i. Title: "Create New Folder"
                  ii. Input field: name_field
                  iii. Status text: loading_text
                  iv. Action Row:
                      - Cancel: pops overlay, updates
                      - Create: calls create handler
                  v. Dimensions: 350x200px
                  vi. White background, rounded
            
            4. **Show Dialog**:
               a. Append to dash.page.overlay
               b. Call dash.page.update()

        Interactions:
            - **DriveService.create_folder()**: API folder creation
            - **create_folder_item()**: UI component creation
            - **DriveService._invalidate_cache()**: Cache management
            - **Dashboard.current_folder_id**: Parent folder tracking
            - **ft.TextField**: Input control

        Example:
            >>> # User clicks "New Folder" button
            >>> file_manager.create_new_folder_dialog()
            >>> # Dialog appears with input field focused
            >>> 
            >>> # User enters "My New Folder" and clicks Create
            >>> # → Shows: "Creating folder..."
            >>> # → API: create_folder("My New Folder", current_folder_id)
            >>> # → Returns: {'id': 'new_123', 'name': 'My New Folder'}
            >>> # → Creates folder item UI component
            >>> # → Inserts at position 1 in list (below back button)
            >>> # → Cache invalidated for current folder
            >>> # → Dialog closes
            >>> # → New folder visible in list immediately
            >>> 
            >>> # Empty name (validation failure)
            >>> # User clicks Create with empty field
            >>> # → Nothing happens (early return)
            >>> 
            >>> # API failure
            >>> # API returns None (error occurred)
            >>> # → Shows: "Failed to create folder."
            >>> # → Dialog stays open
            >>> # → User can retry or cancel

        See Also:
            - :meth:`create_folder_item`: UI component creation
            - :meth:`~services.drive_service.DriveService.create_folder`: API method
            - :meth:`~ui.dashboard.Dashboard.current_folder_id`: State tracking

        Notes:
            - Optimistic UI update (shows before full refresh)
            - Validates non-empty name
            - Loading message during API call
            - Inserts at position 1 (after back button)
            - Cache invalidation ensures consistency
            - Dialog stays open on failure (retry possible)
            - New folders start with 0 subfolders
            - Modal blocks interaction during creation
        """
        name_field = ft.TextField(label="Folder name", autofocus=True)
        loading_text = ft.Text("")

        def create(e):
            folder_name = name_field.value.strip()
            if not folder_name:
                return
            loading_text.value = "Creating folder..."
            self.dash.page.update()

            folder = self.dash.drive.create_folder(folder_name, parent_id=self.dash.current_folder_id)
            if folder:
                self.dash.page.overlay.pop()
                new_folder_item = self.create_folder_item({
                    'id': folder['id'],
                    'name': folder['name'],
                    'mimeType': 'application/vnd.google-apps.folder'
                }, 0)
                insert_position = 1
                if len(self.dash.folder_list.controls) > insert_position:
                    self.dash.folder_list.controls.insert(insert_position, new_folder_item)
                else:
                    self.dash.folder_list.controls.append(new_folder_item)

                self.dash.drive._invalidate_cache(self.dash.current_folder_id)
                self.dash.page.update()
            else:
                loading_text.value = "Failed to create folder."
                self.dash.page.update()

        dialog_container = ft.Container(
            content=ft.Column([
                ft.Text("Create New Folder"),
                name_field,
                loading_text,
                ft.Row([
                    ft.TextButton("Cancel", on_click=lambda e: (self.dash.page.overlay.pop(), self.dash.page.update())),
                    ft.ElevatedButton("Create", on_click=create),
                ], alignment=ft.MainAxisAlignment.END),
            ]),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            width=350,
            height=200,
        )

        self.dash.page.overlay.append(dialog_container)
        self.dash.page.update()
    
    def select_file_to_upload(self):
        """Open system file picker for uploading files to Drive.

        Displays native OS file selection dialog. User can select one or
        multiple files. All selected files uploaded to current Drive folder
        and Dashboard refreshed to show new files.

        Returns:
            None: Opens picker and handles uploads as side effects.

        Algorithm:
            1. **Define Result Handler**:
               a. Check if files selected:
                  i. If e.files is empty or None:
                     - Return early (user cancelled)
               b. Upload each file:
                  i. For each file in e.files:
                     - Get file path: f.path
                     - Call dash.drive.upload_file():
                       - file_path: f.path (local path)
                       - parent_id: dash.current_folder_id
                     - Upload blocks until complete
               c. Refresh Dashboard:
                  i. Call dash.refresh_folder_contents()
                  ii. Shows newly uploaded files
            
            2. **Create File Picker**:
               a. Instantiate ft.FilePicker with:
                  i. on_result: result handler function
               b. Picker tied to handler
            
            3. **Register and Show**:
               a. Append picker to dash.page.overlay
               b. Call dash.page.update() (makes picker available)
               c. Call file_picker.pick_files()
                  i. Opens native file dialog
                  ii. User selects files
                  iii. Dialog closes
                  iv. Result handler called with selection

        Interactions:
            - **ft.FilePicker**: System file selection dialog
            - **DriveService.upload_file()**: Upload operation
            - **Dashboard.refresh_folder_contents()**: UI refresh
            - **Dashboard.current_folder_id**: Upload destination
            - **dash.page.overlay**: Picker registration

        Example:
            >>> # User clicks "Upload" button
            >>> file_manager.select_file_to_upload()
            >>> # Native file picker opens
            >>> 
            >>> # User selects single file
            >>> # → Result: [FilePickerFile(path='C:/docs/report.pdf')]
            >>> # → Upload: upload_file('C:/docs/report.pdf', current_folder_id)
            >>> # → Refresh: Dashboard shows new file
            >>> 
            >>> # User selects multiple files
            >>> # → Result: [file1, file2, file3]
            >>> # → Uploads all files sequentially
            >>> # → Refresh once after all complete
            >>> 
            >>> # User cancels
            >>> # → Result: e.files = None or []
            >>> # → Early return, no uploads

        See Also:
            - :meth:`~services.drive_service.DriveService.upload_file`: Upload method
            - :meth:`~ui.dashboard.Dashboard.refresh_folder_contents`: Refresh
            - :class:`ft.FilePicker`: Flet file picker control

        Notes:
            - Uses native OS file picker
            - Supports multiple file selection
            - Uploads to current folder
            - Sequential upload (one at a time)
            - Refresh after all uploads complete
            - Cancel safe (early return)
            - Files must be readable
            - Large files may take time
            - No progress indicator during upload
            - Picker must be in overlay to work
        """
        def on_result(e: ft.FilePickerResultEvent):
            if not e.files:
                return
            for f in e.files:
                self.dash.drive.upload_file(f.path, parent_id=self.dash.current_folder_id)
            self.dash.refresh_folder_contents()

        file_picker = ft.FilePicker(on_result=on_result)
        self.dash.page.overlay.append(file_picker)
        self.dash.page.update()
        file_picker.pick_files()