"""Paste Links Manager Module.

This module handles the functionality for pasting and processing Google Drive
links (files and folders), managing saved links history, and displaying
the paste links UI view.

Classes:
    PasteLinksManager: Manages link processing, saving, and UI rendering.

See Also:
    :class:`~src.ui.dashboard.Dashboard`: Connects this manager to the UI.
"""

import flet as ft
import json
import os

from utils.common import show_snackbar

SAVED_LINKS_FILE = "saved_links.json"


class PasteLinksManager:
    """Drive link paste and management system with persistent history.

    PasteLinksManager provides functionality for pasting Google Drive URLs,
    resolving them to files/folders, saving valid links to local JSON storage,
    and managing a persistent history of accessed Drive items. It creates a
    dedicated "Paste Links" view in the Dashboard with input field, saved links
    list, and quick access to previously opened Drive resources.
    
    This class implements a link resolution system that accepts various Drive URL
    formats, validates accessibility, extracts metadata, and provides direct
    navigation to folders or preview for files. The saved links feature acts as
    a bookmark system, persisting across application sessions for quick access
    to frequently used Drive resources.

    Purpose:
        - Parse and resolve Google Drive URLs to file/folder IDs
        - Validate Drive link accessibility via API
        - Save validated links to persistent JSON storage
        - Load and display saved links history
        - Provide UI for link input and management
        - Navigate to folders or preview files from links
        - Delete saved links from history
        - Handle multiple Drive URL formats

    Attributes:
        dash (Dashboard): Reference to parent Dashboard instance. Provides access
            to page, drive service, folder_navigator, file_manager, paste_link_field
            input control, and current_view state tracking.
        file_preview (FilePreviewService or None): Service for displaying file
            previews. Handles images, text, PDFs, Office docs. None if service
            import fails (graceful degradation with fallback to file info).

    Interactions:
        - **Dashboard**: Parent container managing state and UI
        - **DriveService**: Resolves links and fetches metadata (via dash.drive)
        - **FilePreviewService**: Displays file previews in modal
        - **FolderNavigator**: Navigates to folders (via dash.folder_navigator)
        - **FileManager**: Shows file info fallback (via dash.file_manager)
        - **JSON file**: Persistent storage (saved_links.json)
        - **ft.TextField**: Link input field (dash.paste_link_field)
        - **ft.SnackBar**: User feedback messages

    Algorithm (High-Level Workflow):
        **Phase 1: Initialization**
            1. Store Dashboard reference
            2. Import FilePreviewService (graceful failure)
            3. Initialize preview service with page and drive
            4. Ready to manage links
        
        **Phase 2: View Loading** (load_paste_links_view)
            1. Set current_view = "paste_links"
            2. Clear folder_list UI
            3. Build header section
            4. Build paste section:
               a. Input field for URL
               b. "Open Link" button
               c. Help text with format examples
            5. Build saved links section:
               a. "Saved Links" header
               b. List of saved link items (cards)
            6. Update page to display
        
        **Phase 3: Link Pasting** (handle_paste_link)
            1. User pastes Drive URL and clicks "Open Link"
            2. Validate non-empty input
            3. Show "Loading..." snackbar
            4. Resolve link via drive.resolve_drive_link():
               a. Extract file/folder ID from URL
               b. Fetch metadata from Drive API
               c. Return (file_id, info) or (None, None)
            5. If invalid:
               a. Show error snackbar
               b. Return early
            6. If valid:
               a. Save to history (add_saved_link)
               b. Show success/already-saved snackbar
               c. Route based on type:
                  - Folder → Navigate via folder_navigator
                  - File → Preview or show info
            7. Clear input field
            8. Refresh view if still active
        
        **Phase 4: Saved Link Management**
            1. Load saved links from JSON file
            2. Check for duplicates (by ID)
            3. Add new link to list
            4. Save updated list to JSON
            5. Display in UI as clickable cards
        
        **Phase 5: Link Opening** (open_saved_link)
            1. User clicks saved link card
            2. Check MIME type:
               a. Folder → Navigate to contents
               b. File → Preview or show info
            3. Update UI accordingly
        
        **Phase 6: Link Deletion** (delete_saved_link)
            1. User clicks delete button on card
            2. Load current links
            3. Filter out deleted item
            4. Save updated list
            5. Refresh view if active

    Example:
        >>> # Initialize in Dashboard
        >>> from ui.dashboard_modules.paste_links_manager import PasteLinksManager
        >>> paste_manager = PasteLinksManager(dashboard)
        >>> 
        >>> # Load paste links view
        >>> paste_manager.load_paste_links_view()
        >>> # Shows input field and saved links
        >>> 
        >>> # User pastes folder link
        >>> dashboard.paste_link_field.value = "https://drive.google.com/drive/folders/abc123"
        >>> paste_manager.handle_paste_link(event)
        >>> # Resolves link → Saves to history → Navigates to folder
        >>> 
        >>> # User pastes file link
        >>> dashboard.paste_link_field.value = "https://drive.google.com/file/d/xyz789/view"
        >>> paste_manager.handle_paste_link(event)
        >>> # Resolves link → Saves to history → Opens preview
        >>> 
        >>> # Access saved link
        >>> saved_links = paste_manager.load_saved_links()
        >>> print(saved_links)
        >>> [
        ...     {'id': 'abc123', 'name': 'Shared Folder', 'mimeType': '...folder', 'url': '...'},
        ...     {'id': 'xyz789', 'name': 'Document.pdf', 'mimeType': 'application/pdf', 'url': '...'}
        ... ]
        >>> 
        >>> # Open saved link
        >>> paste_manager.open_saved_link(saved_links[0])
        >>> # Navigates to folder
        >>> 
        >>> # Delete saved link
        >>> paste_manager.delete_saved_link(saved_links[1])
        >>> # Removes from history and refreshes view

    See Also:
        - :class:`~ui.dashboard.Dashboard`: Parent container
        - :class:`~services.drive_service.DriveService`: Link resolution
        - :class:`~services.file_preview_service.FilePreviewService`: File preview
        - :class:`~ui.dashboard_modules.folder_navigator.FolderNavigator`: Folder navigation
        - :class:`~ui.dashboard_modules.file_manager.FileManager`: File info fallback

    Notes:
        - Saved links persist in saved_links.json
        - Supports multiple Drive URL formats
        - Duplicate detection by file ID
        - Graceful degradation without preview service
        - JSON file created automatically if missing
        - View refreshes after link operations
        - Snackbar feedback for all operations
        - Click card to open, click delete icon to remove

    Supported URL Formats:
        - Folder: https://drive.google.com/drive/folders/FOLDER_ID
        - File: https://drive.google.com/file/d/FILE_ID/view
        - Query: https://drive.google.com/...?id=ID
        - Other formats extracted by DriveService

    Storage Format (saved_links.json):
        ```json
        {
          "links": [
            {
              "id": "file_or_folder_id",
              "name": "Display Name",
              "mimeType": "application/vnd.google-apps.folder",
              "url": "https://drive.google.com/..."
            }
          ]
        }
        ```

    Design Patterns:
        - **Repository**: JSON file as data repository
        - **Facade**: Simplifies link management
        - **Strategy**: Different handling for folders vs files

    References:
        - Google Drive URLs: https://developers.google.com/drive/api/v3/manage-sharing
        - JSON Storage: https://docs.python.org/3/library/json.html
    """

    def __init__(self, dashboard):
        """Initialize PasteLinksManager with Dashboard and preview service.

        Sets up link management capabilities by storing Dashboard reference
        and initializing FilePreviewService. Handles import failure gracefully.

        Args:
            dashboard (Dashboard): Parent Dashboard instance providing access to:
                - page: Flet page for updates
                - drive: DriveService for link resolution
                - folder_navigator: For folder navigation
                - file_manager: For file info display
                - paste_link_field: Input control for URLs
                - current_view: View state tracking

        Algorithm:
            1. **Store Dashboard Reference**:
               a. Assign dashboard parameter to self.dash
               b. All Dashboard services accessed via dash
            
            2. **Initialize Preview Service**:
               a. Enter try block for graceful failure
               b. Import FilePreviewService from services module
               c. Instantiate with dashboard.page and dashboard.drive
               d. Store in self.file_preview
            
            3. **Handle Import Failure**:
               a. Catch ImportError if service unavailable
               b. Set self.file_preview = None
               c. Preview disabled, falls back to file info
               d. No error raised (graceful degradation)

        Interactions:
            - **Dashboard**: Stores reference
            - **FilePreviewService**: Initializes if available

        Example:
            >>> # Standard initialization
            >>> dashboard = Dashboard(page, auth_service)
            >>> paste_manager = PasteLinksManager(dashboard)
            >>> print(paste_manager.file_preview)
            <FilePreviewService instance>
            >>> 
            >>> # Preview service unavailable
            >>> paste_manager = PasteLinksManager(dashboard)
            >>> print(paste_manager.file_preview)
            None
            >>> # Manager still functional, uses file info

        See Also:
            - :class:`~ui.dashboard.Dashboard`: Parent container
            - :class:`~services.file_preview_service.FilePreviewService`: Preview service

        Notes:
            - Dashboard must be initialized first
            - Preview service optional (graceful degradation)
            - No exceptions raised on initialization
            - file_preview checked before use
        """
        self.dash = dashboard
        
        try:
            from services.file_preview_service import FilePreviewService
            self.file_preview = FilePreviewService(dashboard.page, dashboard.drive)
        except ImportError:
            self.file_preview = None
    
    def load_saved_links(self):
        """Load saved Drive links from persistent JSON storage.

        Reads saved_links.json file and returns list of previously saved
        Drive links. Creates empty list if file doesn't exist or on errors.

        Returns:
            list[dict]: List of saved link dictionaries, each containing:
                - 'id' (str): Drive file or folder ID
                - 'name' (str): Display name for link
                - 'mimeType' (str): MIME type (folder or file type)
                - 'url' (str): Original pasted URL
                Returns empty list [] if file missing or error occurs.

        Algorithm:
            1. **Check File Existence**:
               a. Check if SAVED_LINKS_FILE exists
               b. If not exists, return empty list []
            
            2. **Try Loading File**:
               a. Enter try block for error handling
               b. Open SAVED_LINKS_FILE in read mode
               c. Specify UTF-8 encoding
               d. Parse JSON content with json.load()
               e. Store in data variable
            
            3. **Extract Links**:
               a. Get 'links' key from data dict
               b. Use .get("links", []) for safe access
               c. Return links list
            
            4. **Handle Errors**:
               a. Catch any Exception (parse, read, etc.)
               b. Print error message with exception
               c. Return empty list [] (graceful failure)
            
            5. **Default Return**:
               a. If file doesn't exist
               b. Return empty list []

        Interactions:
            - **os.path.exists()**: File existence check
            - **json.load()**: JSON parsing
            - **File I/O**: Opens and reads file

        Example:
            >>> # Load existing links
            >>> links = paste_manager.load_saved_links()
            >>> print(links)
            [
                {
                    'id': 'abc123',
                    'name': 'Project Folder',
                    'mimeType': 'application/vnd.google-apps.folder',
                    'url': 'https://drive.google.com/drive/folders/abc123'
                },
                {
                    'id': 'xyz789',
                    'name': 'Document.pdf',
                    'mimeType': 'application/pdf',
                    'url': 'https://drive.google.com/file/d/xyz789/view'
                }
            ]
            >>> 
            >>> # No saved links (file doesn't exist)
            >>> links = paste_manager.load_saved_links()
            >>> print(links)
            []
            >>> 
            >>> # Corrupted JSON file
            >>> links = paste_manager.load_saved_links()
            >>> # Prints: "Error loading saved links: ..."
            >>> print(links)
            []

        See Also:
            - :meth:`save_saved_links`: Saves links to file
            - :meth:`add_saved_link`: Adds new link
            - :meth:`build_saved_links_ui`: Displays links

        Notes:
            - File: saved_links.json (module constant)
            - UTF-8 encoding for international characters
            - Graceful failure returns empty list
            - No file created by this method
            - JSON structure: {"links": [...]}
        """
        if os.path.exists(SAVED_LINKS_FILE):
            try:
                with open(SAVED_LINKS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("links", [])
            except Exception as e:
                print(f"Error loading saved links: {e}")
                return []
        return []
    
    def save_saved_links(self, links):
        """Save Drive links list to persistent JSON storage.

        Writes provided links list to saved_links.json file, replacing
        existing content. Creates file if doesn't exist.

        Args:
            links (list[dict]): List of link dictionaries to save. Each dict
                should contain 'id', 'name', 'mimeType', 'url' keys. Can be
                empty list to clear saved links.

        Returns:
            None: Writes to file as side effect. Prints error on failure.

        Algorithm:
            1. **Try Saving File**:
               a. Enter try block for error handling
               b. Open SAVED_LINKS_FILE in write mode ('w')
               c. Specify UTF-8 encoding
               d. Use context manager for automatic closing
            
            2. **Write JSON**:
               a. Create dict: {"links": links}
               b. Call json.dump() with:
                  i. data: dict with links
                  ii. file handle: f
                  iii. indent: 2 (pretty print)
               c. Writes formatted JSON to file
            
            3. **Handle Errors**:
               a. Catch any Exception (write, permission, etc.)
               b. Print error message with exception
               c. File may not be updated

        Interactions:
            - **json.dump()**: JSON serialization
            - **File I/O**: Opens and writes file

        Example:
            >>> # Save links list
            >>> links = [
            ...     {
            ...         'id': 'abc123',
            ...         'name': 'Folder',
            ...         'mimeType': 'application/vnd.google-apps.folder',
            ...         'url': 'https://...'
            ...     }
            ... ]
            >>> paste_manager.save_saved_links(links)
            >>> # File updated with links
            >>> 
            >>> # Clear saved links
            >>> paste_manager.save_saved_links([])
            >>> # File now contains: {"links": []}
            >>> 
            >>> # Permission error
            >>> paste_manager.save_saved_links(links)
            >>> # Prints: "Error saving saved links: ..."

        See Also:
            - :meth:`load_saved_links`: Loads links from file
            - :meth:`add_saved_link`: Adds single link
            - :meth:`delete_saved_link`: Removes link

        Notes:
            - Overwrites existing file content
            - indent=2 for readable JSON
            - UTF-8 encoding for compatibility
            - Creates file if doesn't exist
            - Silent failure (prints error only)
            - No return value
        """
        try:
            with open(SAVED_LINKS_FILE, "w", encoding="utf-8") as f:
                json.dump({"links": links}, f, indent=2)
        except Exception as e:
            print(f"Error saving saved links: {e}")
    
    def add_saved_link(self, file_id, info, original_url):
        """Add new Drive link to saved history if not duplicate.

        Appends validated Drive link to saved links list, checking for
        duplicates by file ID. Saves updated list to JSON storage.

        Args:
            file_id (str): Drive file or folder ID. Used for duplicate detection.
            info (dict): File metadata from Drive API containing:
                - 'name' (str): Display name
                - 'mimeType' (str): MIME type
                Additional keys may be present but not used.
            original_url (str): Original pasted URL for reference and re-access.

        Returns:
            bool: True if link was added (new), False if already exists (duplicate).

        Algorithm:
            1. **Load Current Links**:
               a. Call self.load_saved_links()
               b. Returns list of existing links
            
            2. **Check for Duplicate**:
               a. Use any() with generator expression
               b. Check if any link has matching ID
               c. Expression: any(l.get("id") == file_id for l in links)
               d. If duplicate found:
                  i. Return False (not added)
            
            3. **Append New Link**:
               a. Create link dict:
                  i. id: file_id
                  ii. name: info.get("name", file_id) (fallback to ID)
                  iii. mimeType: info.get("mimeType", "") (empty if missing)
                  iv. url: original_url
               b. Append dict to links list
            
            4. **Save Updated List**:
               a. Call self.save_saved_links(links)
               b. Persists to JSON file
            
            5. **Return Success**:
               a. Return True (link added)

        Interactions:
            - **load_saved_links()**: Retrieves current list
            - **save_saved_links()**: Persists updated list

        Example:
            >>> # Add new link
            >>> info = {
            ...     'name': 'Project Folder',
            ...     'mimeType': 'application/vnd.google-apps.folder'
            ... }
            >>> added = paste_manager.add_saved_link(
            ...     'abc123',
            ...     info,
            ...     'https://drive.google.com/drive/folders/abc123'
            ... )
            >>> print(added)
            True
            >>> 
            >>> # Try adding same link again (duplicate)
            >>> added = paste_manager.add_saved_link(
            ...     'abc123',
            ...     info,
            ...     'https://drive.google.com/drive/folders/abc123'
            ... )
            >>> print(added)
            False
            >>> 
            >>> # Add file link
            >>> file_info = {'name': 'Doc.pdf', 'mimeType': 'application/pdf'}
            >>> added = paste_manager.add_saved_link('xyz789', file_info, 'https://...')
            >>> print(added)
            True

        See Also:
            - :meth:`load_saved_links`: Retrieves existing links
            - :meth:`save_saved_links`: Persists to storage
            - :meth:`handle_paste_link`: Calls this after validation

        Notes:
            - Duplicate detection by file ID only
            - Same ID with different URL still considered duplicate
            - Name fallback to ID if missing
            - MIME type empty string if missing
            - Original URL preserved for reference
            - Returns bool for feedback to caller
        """
        links = self.load_saved_links()
        if any(l.get("id") == file_id for l in links):
            return False
        links.append({
            "id": file_id,
            "name": info.get("name", file_id),
            "mimeType": info.get("mimeType", ""),
            "url": original_url,
        })
        self.save_saved_links(links)
        return True
    
    def delete_saved_link(self, item):
        """Remove specific Drive link from saved history.

        Deletes link matching provided item's ID from saved links list,
        saves updated list, and refreshes view if currently active.

        Args:
            item (dict): Link item to remove. Must contain 'id' key for
                matching. Other keys (name, mimeType, url) ignored for
                deletion but typically present.

        Returns:
            None: Updates storage and optionally refreshes view as side effects.

        Algorithm:
            1. **Load Current Links**:
               a. Call self.load_saved_links()
               b. Returns list of all saved links
            
            2. **Filter Out Item**:
               a. Use list comprehension
               b. Keep links where ID doesn't match item's ID
               c. Expression: [l for l in links if l.get("id") != item.get("id")]
               d. Creates new list without deleted item
            
            3. **Save Updated List**:
               a. Call self.save_saved_links(links)
               b. Persists filtered list to JSON
            
            4. **Refresh View** (if active):
               a. Check if dash.current_view == "paste_links"
               b. If yes (paste links view is active):
                  i. Call self.load_paste_links_view()
                  ii. Refreshes UI to show updated list
               c. If no (different view active):
                  i. No refresh needed (silent update)

        Interactions:
            - **load_saved_links()**: Retrieves current list
            - **save_saved_links()**: Persists filtered list
            - **load_paste_links_view()**: Refreshes UI

        Example:
            >>> # Delete saved link
            >>> saved_links = paste_manager.load_saved_links()
            >>> item_to_delete = saved_links[0]
            >>> print(item_to_delete)
            {'id': 'abc123', 'name': 'Old Folder', 'mimeType': '...', 'url': '...'}
            >>> 
            >>> paste_manager.delete_saved_link(item_to_delete)
            >>> # Link removed from storage
            >>> # View refreshed if currently displayed
            >>> 
            >>> # Verify deletion
            >>> updated_links = paste_manager.load_saved_links()
            >>> print(len(updated_links))
            # One less than before
            >>> 
            >>> # Delete from different view
            >>> dashboard.current_view = "your_folders"
            >>> paste_manager.delete_saved_link(item_to_delete)
            >>> # Link deleted but no view refresh (not active)

        See Also:
            - :meth:`load_saved_links`: Retrieves links
            - :meth:`save_saved_links`: Persists changes
            - :meth:`load_paste_links_view`: Refreshes view
            - :meth:`build_saved_links_ui`: Creates delete buttons

        Notes:
            - Deletes by ID match (exact)
            - Safe if item doesn't exist (no error)
            - Refreshes view only if currently active
            - Immediate persistence to JSON
            - Called from delete button in UI
        """
        links = self.load_saved_links()
        links = [l for l in links if l.get("id") != item.get("id")]
        self.save_saved_links(links)
        
        if self.dash.current_view == "paste_links":
            self.load_paste_links_view()
    
    def open_saved_link(self, item):
        """Open saved Drive link (navigate folder or preview file).

        Routes saved link to appropriate handler based on type: navigates
        to folder contents or opens file preview/info dialog.

        Args:
            item (dict): Saved link item containing:
                - 'id' (str): Drive file or folder ID
                - 'name' (str): Display name
                - 'mimeType' (str): MIME type for routing
                Additional keys may be present.

        Returns:
            None: Performs navigation or preview as side effect.

        Algorithm:
            1. **Check Item Type**:
               a. Get mimeType: item.get("mimeType")
               b. Compare to folder MIME type
            
            2. **Handle Folder**:
               a. If mimeType == "application/vnd.google-apps.folder":
                  i. Extract folder ID: item["id"]
                  ii. Extract name: item.get("name", item["id"]) (fallback)
                  iii. Call dash.folder_navigator.show_folder_contents():
                       - folder_id: extracted ID
                       - folder_name: extracted name
                  iv. Navigates to folder view
                  v. Return (routing complete)
            
            3. **Handle File** (else branch):
               a. Check if preview service available
               b. If self.file_preview exists:
                  i. Call file_preview.show_preview() with:
                     - file_id: item["id"]
                     - file_name: item.get("name", "File")
                  ii. Opens preview modal
               c. Else (no preview service):
                  i. Fetch full info: dash.drive.get_file_info(item["id"])
                  ii. If info retrieved:
                      - Call dash.file_manager.show_file_info(info)
                      - Shows metadata dialog
                  iii. If info fetch failed:
                       - Create error snackbar
                       - Message: "Failed to open saved link"
                       - Set open=True
                       - Assign to dash.page.snack_bar
                       - Call dash.page.update()

        Interactions:
            - **FolderNavigator.show_folder_contents()**: Folder navigation
            - **FilePreviewService.show_preview()**: File preview
            - **DriveService.get_file_info()**: Metadata fetch
            - **FileManager.show_file_info()**: Info dialog
            - **ft.SnackBar**: Error feedback

        Example:
            >>> # Open folder link
            >>> folder_item = {
            ...     'id': 'abc123',
            ...     'name': 'Project Files',
            ...     'mimeType': 'application/vnd.google-apps.folder'
            ... }
            >>> paste_manager.open_saved_link(folder_item)
            >>> # Navigates to folder contents
            >>> 
            >>> # Open file link (with preview)
            >>> file_item = {
            ...     'id': 'xyz789',
            ...     'name': 'Report.pdf',
            ...     'mimeType': 'application/pdf'
            ... }
            >>> paste_manager.open_saved_link(file_item)
            >>> # Opens PDF preview modal
            >>> 
            >>> # Open file (no preview service)
            >>> paste_manager.file_preview = None
            >>> paste_manager.open_saved_link(file_item)
            >>> # Fetches info and shows metadata dialog
            >>> 
            >>> # Error case (file not accessible)
            >>> paste_manager.open_saved_link(file_item)
            >>> # Shows: "Failed to open saved link" snackbar

        See Also:
            - :meth:`~ui.dashboard_modules.folder_navigator.FolderNavigator.show_folder_contents`: Folder handler
            - :meth:`~services.file_preview_service.FilePreviewService.show_preview`: Preview display
            - :meth:`~ui.dashboard_modules.file_manager.FileManager.show_file_info`: Info fallback

        Notes:
            - Routing by MIME type
            - Folders always navigable
            - Files preview or show info
            - Graceful degradation without preview
            - Error snackbar on fetch failure
            - Called from saved link UI clicks
        """
        if item.get("mimeType") == "application/vnd.google-apps.folder":
            self.dash.folder_navigator.show_folder_contents(item["id"], item.get("name", item["id"]))
        else:
            if self.file_preview:
                self.file_preview.show_preview(
                    file_id=item["id"],
                    file_name=item.get("name", "File")
                )
            else:
                info = self.dash.drive.get_file_info(item["id"])
                if info:
                    self.dash.file_manager.show_file_info(info)
                else:
                    show_snackbar(self.dash.page, ft.Text("Failed to open saved link"), ft.Colors.RED)

    
    def load_paste_links_view(self):
        """Render Paste Drive Links view with input and saved history.

        Builds and displays complete paste links interface including header,
        input section with help text, and saved links list. Clears previous
        view and updates Dashboard state.

        Returns:
            None: Updates Dashboard folder_list and page as side effects.

        Algorithm:
            1. **Set View State**:
               a. Set dash.current_view = "paste_links"
               b. Tracks active view for refresh logic
            
            2. **Clear UI**:
               a. Call dash.folder_list.controls.clear()
               b. Removes all previous content
            
            3. **Build Header Section**:
               a. Create ft.Container with:
                  i. Text: "Paste Drive Links" (size 20, bold)
                  ii. padding: 10px
               b. Store in header variable
            
            4. **Build Paste Section**:
               a. Create ft.Container with:
                  i. Column containing:
                      - Instruction text (size 14)
                      - paste_link_field (TextField reference)
                      - "Open Link" button:
                        - on_click: handle_paste_link
                        - bgcolor: BLUE_400
                        - color: WHITE
                        - icon: LINK
                      - Help text showing supported formats:
                        - Folder format
                        - File format
                        - Query parameter format
                        - size 12, grey color
                  ii. spacing: 10px between elements
                  iii. padding: 20px
                  iv. bgcolor: BLUE_50 (light blue background)
                  v. border_radius: 10px (rounded corners)
               b. Store in paste_section variable
            
            5. **Build Saved Links Header**:
               a. Create ft.Container with:
                  i. Text: "Saved Links" (size 16, bold)
                  ii. padding: top=20, bottom=10, left=10
               b. Store in saved_links_header variable
            
            6. **Build Saved Links List**:
               a. Call self.build_saved_links_ui()
               b. Returns Column with link cards
               c. Wrap in ft.Container with padding: 10px
               d. Store in saved_links_list variable
            
            7. **Assemble View**:
               a. Call dash.folder_list.controls.extend() with list:
                  i. header
                  ii. paste_section
                  iii. saved_links_header
                  iv. saved_links_list
               b. Adds all sections to display
            
            8. **Update Display**:
               a. Call dash.page.update()
               b. Renders complete view

        Interactions:
            - **Dashboard.folder_list**: Main display area
            - **Dashboard.paste_link_field**: Input control
            - **build_saved_links_ui()**: Saved links section
            - **ft.Container, ft.Column, ft.Text**: UI components

        Example:
            >>> # Load paste links view
            >>> paste_manager.load_paste_links_view()
            >>> # Dashboard shows:
            >>> # ┌─ Paste Drive Links ─────────────┐
            >>> # │ Paste a Google Drive link:      │
            >>> # │ [_________________________]      │
            >>> # │ [Open Link 🔗]                   │
            >>> # │ Supported formats:               │
            >>> # │ • folders/FOLDER_ID             │
            >>> # │ • file/d/FILE_ID                │
            >>> # │ • ...?id=ID                     │
            >>> # ├─ Saved Links ───────────────────┤
            >>> # │ 📁 Project Folder    [👁][🗑]   │
            >>> # │ 📄 Document.pdf      [👁][🗑]   │
            >>> # └─────────────────────────────────┘

        See Also:
            - :meth:`handle_paste_link`: Input handler
            - :meth:`build_saved_links_ui`: Saved links display
            - :meth:`delete_saved_link`: Refreshes this view

        Notes:
            - Full view replacement (clears previous)
            - Input field referenced from Dashboard
            - Help text with format examples
            - Blue theme for paste section
            - Saved links section separate
            - Called on view switch and refresh
        """
        self.dash.current_view = "paste_links"
        self.dash.folder_list.controls.clear()

        header = ft.Container(
            content=ft.Text("Paste Drive Links", size=20, weight=ft.FontWeight.BOLD),
            padding=10
        )

        paste_section = ft.Container(
            content=ft.Column([
                ft.Text("Paste a Google Drive folder or file link:" , size=14),
                self.dash.paste_link_field,
                ft.ElevatedButton(
                    "Open Link",
                    on_click=self.handle_paste_link,
                    bgcolor=ft.Colors.BLUE_400,
                    color=ft.Colors.WHITE,
                    icon=ft.Icons.LINK
                ),
                ft.Text(
                    "Supported formats:\n"
                    "• https://drive.google.com/drive/folders/FOLDER_ID\n"
                    "• https://drive.google.com/file/d/FILE_ID\n"
                    "• https://drive.google.com/...?id=ID",
                    size=12,
                    color=ft.Colors.GREY_600
                )
            ], spacing=10),
            padding=20,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10
        )

        saved_links_header = ft.Container(
            content=ft.Text("Saved Links", size=16, weight=ft.FontWeight.BOLD),
            padding=ft.padding.only(top=20, bottom=10, left=10)
        )

        saved_links_list = ft.Container(
            content=self.build_saved_links_ui(),
            padding=10
        )

        self.dash.folder_list.controls.extend([
            header,
            paste_section,
            saved_links_header,
            saved_links_list
        ])

        self.dash.page.update()
    
    def handle_paste_link(self, e):
        """Process pasted Drive link with validation, resolution, and routing.

        Validates input, resolves Drive URL to file/folder ID via API,
        saves to history, and opens appropriate view (folder or preview).
        Shows feedback via snackbars throughout process.

        Args:
            e (ft.ControlEvent): Button click event from "Open Link" button.
                Event data not used, link read from dash.paste_link_field.value.

        Returns:
            None: Performs navigation/preview and updates storage as side effects.

        Algorithm:
            1. **Get and Validate Input**:
               a. Read dash.paste_link_field.value
               b. Call .strip() to remove whitespace
               c. Print debug message with link
               d. If empty string:
                  i. Print debug message
                  ii. Return early (no-op)
            
            2. **Show Loading Feedback**:
               a. Create SnackBar: "Loading Drive link..."
               b. Set open=True
               c. Assign to dash.page.snack_bar
               d. Call dash.page.update() to display
            
            3. **Try Link Resolution**:
               a. Enter try block for error handling
               b. Call dash.drive.resolve_drive_link(link)
               c. Returns (file_id, info) or (None, None)
               d. Print debug message with results
            
            4. **Validate Resolution**:
               a. If file_id is None OR info is None:
                  i. Resolution failed
                  ii. Create error snackbar:
                      - Message: "Invalid or inaccessible Drive link"
                      - bgcolor: RED_400
                      - open: True
                  iii. Assign to dash.page.snack_bar
                  iv. Call dash.page.update()
                  v. Return early
            
            5. **Extract Metadata**:
               a. Get mime_type: info.get("mimeType", "")
               b. Get name: info.get("name", "Shared Item")
               c. Print debug message with details
            
            6. **Save to History** (nested try):
               a. Enter try block
               b. Call add_saved_link(file_id, info, link)
               c. Returns bool: saved_added
               d. If saved_added is True:
                  i. Create snackbar: "Saved link"
               e. Else (already exists):
                  i. Create snackbar: "Link already saved"
               f. Assign snackbar to dash.page.snack_bar
               g. Catch Exception if save fails:
                  i. Print error message
            
            7. **Route by Type** - Folder:
               a. If mime_type == "application/vnd.google-apps.folder":
                  i. Create success snackbar:
                     - Message: f"Opening folder: {name}"
                     - bgcolor: GREEN_400
                  ii. Assign to dash.page.snack_bar
                  iii. Call dash.page.update()
                  iv. Call folder_navigator.show_folder_contents(file_id, name)
                  v. Navigates to folder
            
            8. **Route by Type** - File (else):
               a. Check if preview service available
               b. If self.file_preview exists:
                  i. Create info snackbar:
                     - Message: f"Opening preview: {name}"
                     - bgcolor: BLUE_400
                  ii. Assign to dash.page.snack_bar
                  iii. Call dash.page.update()
                  iv. Call file_preview.show_preview(file_id, name)
               c. Else (no preview):
                  i. Create info snackbar:
                     - Message: f"File detected: {name}"
                     - bgcolor: BLUE_400
                  ii. Assign to dash.page.snack_bar
                  iii. Call dash.page.update()
                  iv. Call file_manager.show_file_info(info)
            
            9. **Clear Input**:
               a. Set dash.paste_link_field.value = "" (empty)
               b. Clears input for next link
            
            10. **Handle Errors**:
                a. Catch any Exception in outer try
                b. Print error message with exception
                c. Create error snackbar with exception message
                d. bgcolor: RED_400
                e. Assign to dash.page.snack_bar
            
            11. **Refresh View** (if active):
                a. Check if dash.current_view == "paste_links"
                b. If yes:
                   i. Call load_paste_links_view()
                   ii. Refreshes to show new saved link
            
            12. **Final Update**:
                a. Call dash.page.update()
                b. Ensures all changes rendered

        Interactions:
            - **Dashboard.paste_link_field**: Input control
            - **DriveService.resolve_drive_link()**: URL resolution
            - **add_saved_link()**: History persistence
            - **FolderNavigator.show_folder_contents()**: Folder navigation
            - **FilePreviewService.show_preview()**: File preview
            - **FileManager.show_file_info()**: Info fallback
            - **ft.SnackBar**: User feedback

        Example:
            >>> # Valid folder link
            >>> dashboard.paste_link_field.value = "https://drive.google.com/drive/folders/abc123"
            >>> paste_manager.handle_paste_link(event)
            >>> # Shows: "Loading Drive link..."
            >>> # Shows: "Saved link"
            >>> # Shows: "Opening folder: Project Files"
            >>> # Navigates to folder
            >>> 
            >>> # Valid file link (preview available)
            >>> dashboard.paste_link_field.value = "https://drive.google.com/file/d/xyz789/view"
            >>> paste_manager.handle_paste_link(event)
            >>> # Shows: "Opening preview: Document.pdf"
            >>> # Opens preview modal
            >>> 
            >>> # Invalid link
            >>> dashboard.paste_link_field.value = "https://invalid-url.com"
            >>> paste_manager.handle_paste_link(event)
            >>> # Shows: "Invalid or inaccessible Drive link"
            >>> 
            >>> # Already saved link
            >>> dashboard.paste_link_field.value = "https://drive.google.com/drive/folders/abc123"
            >>> paste_manager.handle_paste_link(event)
            >>> # Shows: "Link already saved"
            >>> # Still opens folder

        See Also:
            - :meth:`~services.drive_service.DriveService.resolve_drive_link`: URL parsing
            - :meth:`add_saved_link`: History persistence
            - :meth:`load_paste_links_view`: View refresh

        Notes:
            - Multiple snackbar feedback points
            - Debug prints throughout (development aid)
            - Graceful error handling at multiple levels
            - Input cleared on success
            - View refreshed if currently active
            - Preview or info fallback for files
            - Duplicate detection during save
            - Empty input returns early (silent)
        """
        link = self.dash.paste_link_field.value.strip()
        print(f"DEBUG: handle_paste_link called with: {link}")

        if not link:
            print("DEBUG: Empty link")
            return
        
        show_snackbar(self.dash.page, "Loading Drive link...", ft.Colors.BLUE)
        

        try:
            file_id, info = self.dash.drive.resolve_drive_link(link)

            print(f"DEBUG: file_id={file_id}, info={info}")

            if not file_id or not info:
                show_snackbar(self.dash.page, "Invalid or inaccessible Drive link", ft.Colors.RED)
                return

            mime_type = info.get("mimeType", "")
            name = info.get("name", "Shared Item")

            print(f"DEBUG: mime_type={mime_type}, name={name}")

            try:
                saved_added = self.add_saved_link(file_id, info, link)
                if saved_added:
                    show_snackbar(self.dash.page, "Link saved", ft.Colors.GREEN)
                else:
                    show_snackbar(self.dash.page, "Link already saved", ft.Colors.ORANGE)
            except Exception as ex:
                print(f"ERROR: Failed to save link: {ex}")

            if mime_type == "application/vnd.google-apps.folder":
                show_snackbar(self.dash.page, f"Opening folder: {name}", ft.Colors.GREEN)
                self.dash.folder_navigator.show_folder_contents(file_id, name)
            else:
                if self.file_preview:
                    show_snackbar(self.dash.page, f"Opening preview: {name}", ft.Colors.GREEN)
                    self.file_preview.show_preview(file_id=file_id, file_name=name)
                else:
                    show_snackbar(self.dash.page, f"Opening file info: {name}", ft.Colors.GREEN)
                    self.dash.file_manager.show_file_info(info)

            self.dash.paste_link_field.value = ""

        except Exception as ex:
            print(f"ERROR: Exception in handle_paste_link: {ex}")
            show_snackbar(self.dash.page, f"Error processing link: {ex}", ft.Colors.RED)

        if self.dash.current_view == "paste_links":
            self.load_paste_links_view()

        self.dash.page.update()
    
    def build_saved_links_ui(self):
        """Construct UI for saved links list with clickable cards.

        Generates Column containing visual cards for each saved link,
        with icon, name, action buttons (preview/open, delete). Returns
        empty state message if no saved links.

        Returns:
            ft.Column: Column control containing link cards or empty message.
                Each card is Container with Row of Icon, Text, IconButtons.
                Spacing: 4px between cards.

        Algorithm:
            1. **Load Saved Links**:
               a. Call self.load_saved_links()
               b. Returns list of saved link dicts
            
            2. **Create Column**:
               a. Instantiate ft.Column with spacing=4
               b. Store in col variable
            
            3. **Check Empty State**:
               a. If saved list is empty:
                  i. Append Text: "No saved links yet." (grey color)
                  ii. Return col (early return)
            
            4. **Iterate Saved Links**:
               a. For each item in saved:
                  i. Determine item type:
                     - is_folder = (mimeType == "application/vnd.google-apps.folder")
                  ii. Select icon:
                      - If is_folder: icon = FOLDER
                      - Else: icon = DESCRIPTION
            
            5. **Build Link Card** (for each item):
               a. Create ft.Row with:
                  i. ft.Icon(icon, size=20)
                  ii. ft.Text(item["name"], expand=True)
                  iii. Preview/Open IconButton:
                      - icon: VISIBILITY
                      - tooltip: "Preview" or "Open" based on type
                      - on_click: lambda calls open_saved_link(item)
                      - Only if preview available OR is folder
                      - Else: empty Container
                  iv. Delete IconButton:
                      - icon: DELETE
                      - tooltip: "Delete"
                      - on_click: lambda calls delete_saved_link(item)
               
               b. Wrap Row in ft.Container with:
                  i. content: Row
                  ii. padding: 8px
                  iii. ink: True (ripple effect)
                  iv. on_click: lambda calls open_saved_link(item)
                  v. border: 1px grey border all sides
                  vi. border_radius: 8px (rounded)
               
               c. Append container to col.controls
            
            6. **Return Column**:
               a. Return col with all link cards

        Interactions:
            - **load_saved_links()**: Retrieves link data
            - **open_saved_link()**: Click handler
            - **delete_saved_link()**: Delete handler
            - **ft.Column, ft.Row, ft.Container**: Layout
            - **ft.Icon, ft.Text, ft.IconButton**: UI elements

        Example:
            >>> # Build saved links UI
            >>> ui = paste_manager.build_saved_links_ui()
            >>> # Returns Column with cards:
            >>> # ┌────────────────────────────────┐
            >>> # │ 📁 Project Folder    [👁][🗑] │
            >>> # │ 📄 Document.pdf      [👁][🗑] │
            >>> # │ 📁 Shared Resources  [👁][🗑] │
            >>> # └────────────────────────────────┘
            >>> 
            >>> # No saved links
            >>> ui = paste_manager.build_saved_links_ui()
            >>> # Returns: "No saved links yet."

        See Also:
            - :meth:`load_saved_links`: Data source
            - :meth:`open_saved_link`: Click handler
            - :meth:`delete_saved_link`: Delete handler
            - :meth:`load_paste_links_view`: Uses this UI

        Notes:
            - Empty state friendly message
            - Icon varies by type (folder/file)
            - Preview button conditional (service + file)
            - Delete button always present
            - Card clickable (opens link)
            - Ripple effect on click (ink=True)
            - Rounded borders (8px radius)
            - Lambda captures item for handlers
            - Spacing 4px between cards
        """
        saved = self.load_saved_links()
        col = ft.Column(spacing=4)

        if not saved:
            col.controls.append(ft.Text("No saved links yet.", color=ft.Colors.GREY_600))
            return col

        for item in saved:
            is_folder = item.get("mimeType") == "application/vnd.google-apps.folder"
            icon = ft.Icons.FOLDER if is_folder else ft.Icons.DESCRIPTION

            row = ft.Container(
                content=ft.Row([
                    ft.Icon(icon, size=20),
                    ft.Text(item["name"], expand=True),
                    ft.IconButton(
                        icon=ft.Icons.VISIBILITY,
                        tooltip="Preview" if not is_folder else "Open",
                        on_click=lambda e, it=item: self.open_saved_link(it)
                    ) if not is_folder else ft.Container(),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        tooltip="Delete",
                        on_click=lambda e, it=item: self.delete_saved_link(it)
                    )
                ]),
                padding=8,
                ink=True,
                on_click=lambda e, it=item: self.open_saved_link(it),
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=8
            )

            col.controls.append(row)

        return col