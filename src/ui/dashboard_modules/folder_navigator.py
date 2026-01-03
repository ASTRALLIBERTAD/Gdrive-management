"""Folder Navigator Module.

This module handles filesystem navigation logic for the dashboard,
managing current view state, folder loading, and history navigation.

Classes:
    FolderNavigator: Manages folder browsing and navigation state.

See Also:
    :class:`~src.ui.dashboard.Dashboard`: Main UI connect.
    :class:`~src.services.drive_service.DriveService`: Data source.
"""

import flet as ft


class FolderNavigator:
    """Dashboard folder navigation system with history and breadcrumb management.

    FolderNavigator manages the complete folder browsing experience in the Dashboard,
    including navigation state tracking, folder content loading, back button history
    stack, search functionality, and view switching between My Drive, Shared Drives,
    and Paste Links. It maintains navigation context and coordinates between the
    Dashboard UI and DriveService backend.
    
    This class implements a browser-like navigation pattern with forward navigation
    (clicking folders), backward navigation (back button with history stack), and
    root-level view switching. It handles loading states, error conditions, and
    provides smooth transitions between different folder contexts while maintaining
    user's navigation history for intuitive browsing.

    Purpose:
        - Manage folder navigation state and history
        - Load and display folder contents
        - Handle back button with history stack
        - Switch between view contexts (My Drive, Shared Drives)
        - Execute search queries and display results
        - Refresh folder contents with cache invalidation
        - Coordinate UI updates with Drive API calls
        - Provide loading indicators and error handling

    Attributes:
        dash (Dashboard): Reference to parent Dashboard instance. Provides access
            to current_view, current_folder_id, current_folder_name, folder_stack,
            folder_list UI control, drive service, file_manager, and page for updates.
            All navigation state stored in Dashboard for accessibility.

    Interactions:
        - **Dashboard**: Parent container managing overall state
        - **DriveService**: Backend for Drive API operations (via dash.drive)
        - **FileManager**: Creates file/folder UI items (via dash.file_manager)
        - **ft.Text**: Status messages and headers
        - **ft.IconButton**: Back button control
        - **ft.ProgressRing**: Loading indicators
        - **ft.Row**: Layout for controls and items

    Algorithm (High-Level Workflow):
        **Phase 1: Initialization**
            1. Store Dashboard reference
            2. Access navigation state from Dashboard
            3. Ready to load and navigate folders
        
        **Phase 2: Root View Loading**
            1. User selects view (My Drive/Shared Drives)
            2. Set current_view and current_folder_id
            3. Clear folder_list UI
            4. Fetch root-level contents from Drive
            5. Create UI items for each folder
            6. Update page to display
        
        **Phase 3: Folder Navigation** (Forward)
            1. User clicks folder item
            2. Push current context to history stack
            3. Update current_folder_id and name
            4. Clear folder_list
            5. Add back button if history exists
            6. Show loading indicator
            7. Fetch folder contents from Drive
            8. Create UI items for contents
            9. Remove loading indicator
            10. Update page with new view
        
        **Phase 4: Back Navigation**
            1. User clicks back button
            2. Pop previous context from stack
            3. Restore previous folder_id and name
            4. Route to appropriate loader:
               a. root → load view (My Drive/Shared/Paste)
               b. folder → show_folder_contents
            5. Update page with restored view
        
        **Phase 5: Search Execution**
            1. User submits search query
            2. Call drive.search_files with query
            3. Clear folder_list
            4. Create UI items for results
            5. Update page with search results
        
        **Phase 6: Refresh Operation**
            1. User clicks refresh button
            2. Invalidate cache for current folder
            3. Reload folder contents (no stack push)
            4. Update page with fresh data

    Example:
        >>> # Initialize in Dashboard
        >>> from ui.dashboard_modules.folder_navigator import FolderNavigator
        >>> navigator = FolderNavigator(dashboard)
        >>> 
        >>> # Load My Drive root
        >>> navigator.load_your_folders()
        >>> # Displays root-level folders
        >>> 
        >>> # Navigate into folder
        >>> navigator.show_folder_contents(
        ...     folder_id='folder_abc123',
        ...     folder_name='Documents'
        ... )
        >>> # Shows Documents folder contents
        >>> # Back button appears
        >>> # History stack: [('root', 'My Drive')]
        >>> 
        >>> # Navigate deeper
        >>> navigator.show_folder_contents(
        ...     folder_id='folder_xyz789',
        ...     folder_name='Reports'
        ... )
        >>> # History stack: [('root', 'My Drive'), ('folder_abc123', 'Documents')]
        >>> 
        >>> # Go back
        >>> navigator.go_back()
        >>> # Returns to Documents folder
        >>> # History stack: [('root', 'My Drive')]
        >>> 
        >>> # Search
        >>> dashboard.search_field.value = "budget"
        >>> navigator.handle_search(event)
        >>> # Shows search results for "budget"
        >>> 
        >>> # Refresh current folder
        >>> navigator.refresh_folder_contents()
        >>> # Reloads current folder with fresh data

    See Also:
        - :class:`~ui.dashboard.Dashboard`: Parent container
        - :class:`~services.drive_service.DriveService`: Backend operations
        - :class:`~ui.dashboard_modules.file_manager.FileManager`: UI item creation

    Notes:
        - Navigation state stored in Dashboard (not FolderNavigator)
        - History stack enables back button functionality
        - Root folder ID is "root" (Drive API convention)
        - push_to_stack=False prevents duplicate history entries
        - Loading indicators show during API calls
        - Error messages display on API failures
        - Search queries filter across entire Drive
        - Shared drives treated as special folders
        - Cache invalidation ensures fresh data on refresh

    Navigation State (in Dashboard):
        - current_view: "your_folders", "shared_drives", or "paste_links"
        - current_folder_id: Drive ID of currently displayed folder
        - current_folder_name: Display name for breadcrumb/header
        - folder_stack: List of (id, name) tuples for back navigation

    Design Patterns:
        - **State Pattern**: Different behaviors for different views
        - **Command Pattern**: Navigation actions encapsulated
        - **Memento Pattern**: History stack for navigation state
        - **Facade**: Simplifies complex navigation logic

    References:
        - Browser History API: https://developer.mozilla.org/en-US/docs/Web/API/History
        - Google Drive API: https://developers.google.com/drive/api/v3/reference
        - Material Design Navigation: https://m3.material.io/components/navigation-drawer
    """

    def __init__(self, dashboard):
        """Initialize FolderNavigator with Dashboard reference.

        Sets up navigator with access to Dashboard state and services.
        Navigation state stored in Dashboard for accessibility across modules.

        Args:
            dashboard (Dashboard): Parent Dashboard instance providing access to:
                - current_view: View context string
                - current_folder_id: Active folder ID
                - current_folder_name: Active folder display name
                - folder_stack: History stack for back navigation
                - folder_list: UI control for displaying items
                - drive: DriveService instance
                - file_manager: FileManager instance
                - page: Flet page for updates

        Algorithm:
            1. **Store Dashboard Reference**:
               a. Assign dashboard parameter to self.dash
               b. All navigation state accessed via dash
               c. Services accessed via dash.drive, dash.file_manager

        Interactions:
            - **Dashboard**: Stores reference for state and service access

        Example:
            >>> # Initialization during Dashboard setup
            >>> dashboard = Dashboard(page, auth_service)
            >>> navigator = FolderNavigator(dashboard)
            >>> # Navigator ready to manage folder navigation
            >>> 
            >>> # Access Dashboard state
            >>> current_folder = navigator.dash.current_folder_id
            >>> print(current_folder)
            root

        See Also:
            - :class:`~ui.dashboard.Dashboard`: Parent container
            - :meth:`load_your_folders`: Initial view loading

        Notes:
            - Single Dashboard reference for all operations
            - Navigation state in Dashboard (not navigator)
            - No initialization of state here (Dashboard handles)
            - Lightweight initialization (just reference storage)
        """
        self.dash = dashboard
    
    def load_your_folders(self):
        """Load and display user's My Drive root folder view.

        Resets navigation to My Drive root, fetches root-level folders,
        counts subfolders for each, and displays as list items. Clears
        any previous view and history.

        Returns:
            None: Updates Dashboard folder_list and page as side effects.

        Algorithm:
            1. **Set View Context**:
               a. Set dash.current_view = "your_folders"
               b. Set dash.current_folder_id = "root"
               c. Set dash.current_folder_name = "My Drive"
               d. Establishes root context
            
            2. **Clear UI**:
               a. Call dash.folder_list.controls.clear()
               b. Removes all previous list items
            
            3. **Try Folder Loading**:
               a. Enter try block for error handling
               b. Call dash.drive.list_files("root", page_size=100)
               c. Returns {'files': [...], 'nextPageToken': ...} or None
            
            4. **Handle API Result**:
               a. If result is None:
                  i. API call failed (network error)
                  ii. Append error text: "Failed to load folders."
               b. If result is dict:
                  i. Extract files list: result.get("files", [])
                  ii. Filter folders only:
                      - List comprehension
                      - mimeType == "application/vnd.google-apps.folder"
                  iii. Store in folders list
            
            5. **Process Folders**:
               a. If folders list empty:
                  i. Append message: "No folders found"
               b. Else for each folder:
                  i. Fetch subfolder count:
                     - Call drive.list_files(folder["id"], page_size=100)
                     - Get sub_result
                     - If None: sub_count = 0
                     - Else: Filter for folders, count length
                  ii. Create UI item:
                      - Call file_manager.create_folder_item(folder, sub_count)
                  iii. Append to folder_list.controls
            
            6. **Handle Errors**:
               a. Catch any Exception (network, API, parsing)
               b. Append error message: "Error loading your folders" (RED)
            
            7. **Update Display**:
               a. Call dash.page.update()
               b. Renders all changes to UI

        Interactions:
            - **DriveService.list_files()**: Fetches root and subfolder contents
            - **FileManager.create_folder_item()**: Creates UI components
            - **Dashboard.folder_list**: UI control for display
            - **ft.Text**: Status and error messages

        Example:
            >>> # Load My Drive root view
            >>> navigator.load_your_folders()
            >>> # Dashboard shows:
            >>> # - "Documents" (5 folders)
            >>> # - "Photos" (2 folders)
            >>> # - "Projects" (0 folders)
            >>> 
            >>> # Empty root
            >>> navigator.load_your_folders()
            >>> # Shows: "No folders found"
            >>> 
            >>> # Network error
            >>> navigator.load_your_folders()
            >>> # Shows: "Failed to load folders."

        See Also:
            - :meth:`show_folder_contents`: Navigate into folder
            - :meth:`load_shared_drives`: Alternative root view
            - :meth:`~services.drive_service.DriveService.list_files`: API method

        Notes:
            - Only shows folders (not files) at root level
            - Counts subfolders for each (depth 1 only)
            - Subfolder count may be slow for many folders
            - Clears history and previous view
            - Network errors handled gracefully
            - Empty state shows friendly message
            - Page size 100 (Drive API limit 1000)
        """
        self.dash.current_view = "your_folders"
        self.dash.current_folder_id = "root"
        self.dash.current_folder_name = "My Drive"
        self.dash.folder_list.controls.clear()

        try:
            result = self.dash.drive.list_files("root", page_size=100)
            if result is None:
                self.dash.folder_list.controls.append(ft.Text("Failed to load folders."))
            else:
                files = result.get("files", [])
                
                if not files:
                    self.dash.folder_list.controls.append(ft.Text("No items found"))
                else:
                    
                    folders = [f for f in files if f.get("mimeType") == "application/vnd.google-apps.folder"]
                    for folder in folders:
                        sub_result = self.dash.drive.list_files(folder["id"], page_size=100)
                        sub_count = 0 if sub_result is None else len([
                            f for f in sub_result.get("files", [])
                            if f.get("mimeType") == "application/vnd.google-apps.folder"
                        ])
                        self.dash.folder_list.controls.append(self.dash.file_manager.create_folder_item(folder, sub_count))
                    
                    regular_files = [f for f in files if f.get("mimeType") != "application/vnd.google-apps.folder"]
                    for file in regular_files:
                        self.dash.folder_list.controls.append(self.dash.file_manager.create_file_item(file))
        except:
            self.dash.folder_list.controls.append(ft.Text("Error loading your folders", color=ft.Colors.RED))

        self.dash.page.update()
    
    def show_folder_contents(self, folder_id, folder_name=None, is_shared_drive=False, push_to_stack=True):
        """Display contents of specified folder with back navigation support.

        Main navigation method that loads and displays folder contents,
        manages history stack for back button, shows loading states, and
        handles errors. Updates Dashboard state and UI with folder items.

        Args:
            folder_id (str): Drive ID of folder to display. Use "root" for
                My Drive root. Required parameter for content fetching.
            folder_name (str, optional): Display name for folder header and
                breadcrumb. If None, uses folder_id as fallback. Defaults to None.
            is_shared_drive (bool, optional): Whether folder is within shared
                drive context. May affect permissions and behavior. Defaults to False.
            push_to_stack (bool, optional): Whether to save current context to
                history stack before navigating. Set False for refresh or back
                navigation to prevent duplicate entries. Defaults to True.

        Returns:
            None: Updates Dashboard state, folder_list, and page as side effects.

        Algorithm:
            1. **Determine Display Name**:
               a. If folder_name provided: use folder_name
               b. Else: use folder_id as fallback
               c. Store in display_name
            
            2. **Manage Navigation History**:
               a. If push_to_stack is True:
                  i. Check if current_folder_id != folder_id (not same folder)
                  ii. If different:
                      - Create tuple: (current_folder_id, current_folder_name)
                      - Append to dash.folder_stack
                      - Enables back button
            
            3. **Update Context State**:
               a. Set dash.current_folder_id = folder_id
               b. Set dash.current_folder_name = display_name
               c. Dashboard now tracks new folder
            
            4. **Clear UI**:
               a. Call dash.folder_list.controls.clear()
               b. Removes all previous items
            
            5. **Build Navigation Controls**:
               a. Initialize back_controls = [] (empty list)
               b. If dash.folder_stack has items (history exists):
                  i. Create IconButton:
                     - icon: ARROW_BACK
                     - on_click: lambda calls go_back()
                  ii. Append to back_controls
            
            6. **Create Header Row**:
               a. Create ft.Row with:
                  i. *back_controls (unpacked, may be empty)
                  ii. Text: display_name (size 18, bold)
                  iii. ElevatedButton:
                      - text: "Refresh"
                      - icon: REFRESH
                      - on_click: lambda calls refresh_folder_contents()
                  iv. alignment: SPACE_BETWEEN
               b. Append to folder_list.controls
            
            7. **Show Loading State**:
               a. Create loading_indicator (ft.Row):
                  i. ProgressRing (20x20)
                  ii. Text: "Loading folder contents..." (size 14)
               b. Append to folder_list.controls
               c. Call dash.page.update() to show immediately
            
            8. **Try Loading Contents**:
               a. Enter try block
               b. Call dash.drive.list_files():
                  i. folder_id: target folder
                  ii. page_size: 200 (more items)
                  iii. use_cache: False (fresh data)
               c. Returns result dict or None
            
            9. **Remove Loading Indicator**:
               a. Call folder_list.controls.remove(loading_indicator)
               b. Clears loading state
            
            10. **Handle API Result**:
                a. If result is None:
                   i. Network error occurred
                   ii. Append message: "Network error" (ORANGE)
                b. If result is dict:
                   i. Extract files: result.get("files", [])
                   ii. If files empty:
                       - Append message: "Folder is empty"
                   iii. Else for each file:
                        - Call file_manager.create_file_item(file)
                        - Append to folder_list.controls
            
            11. **Handle Errors**:
                a. Catch any Exception
                b. Append error message: "Error loading folder contents" (RED)
            
            12. **Update Display**:
                a. Call dash.page.update()
                b. Renders final state

        Interactions:
            - **DriveService.list_files()**: Fetches folder contents
            - **FileManager.create_file_item()**: Creates UI items
            - **Dashboard.folder_stack**: History management
            - **ft.IconButton**: Back button
            - **ft.ProgressRing**: Loading indicator

        Example:
            >>> # Navigate into folder
            >>> navigator.show_folder_contents(
            ...     folder_id='folder_abc123',
            ...     folder_name='Documents'
            ... )
            >>> # Shows:
            >>> # [<-] Documents [Refresh]
            >>> # - report.pdf
            >>> # - meeting_notes.txt
            >>> # - subfolder/
            >>> 
            >>> # Refresh current folder (no stack push)
            >>> navigator.show_folder_contents(
            ...     folder_id='folder_abc123',
            ...     folder_name='Documents',
            ...     push_to_stack=False
            ... )
            >>> # Reloads without adding to history
            >>> 
            >>> # Navigate with fallback name
            >>> navigator.show_folder_contents(
            ...     folder_id='folder_xyz789'
            ... )
            >>> # Header shows: folder_xyz789 (ID as name)
            >>> 
            >>> # Shared drive folder
            >>> navigator.show_folder_contents(
            ...     folder_id='shared_folder_123',
            ...     folder_name='Team Resources',
            ...     is_shared_drive=True
            ... )

        See Also:
            - :meth:`go_back`: Back navigation
            - :meth:`refresh_folder_contents`: Refresh wrapper
            - :meth:`~services.drive_service.DriveService.list_files`: API method

        Notes:
            - Loading indicator shows immediately (better UX)
            - Back button only if history exists
            - Refresh button always present
            - push_to_stack=False prevents duplicate history
            - use_cache=False ensures fresh data
            - Page size 200 (larger than root load)
            - Error states handled gracefully
            - Empty folders show friendly message
            - Both files and folders displayed
        """
        display_name = folder_name or folder_id

        if push_to_stack and self.dash.current_folder_id != folder_id:
            self.dash.folder_stack.append((self.dash.current_folder_id, self.dash.current_folder_name))

        self.dash.current_folder_id = folder_id
        self.dash.current_folder_name = display_name

        self.dash.folder_list.controls.clear()

        back_controls = []

        if self.dash.folder_stack:
            back_controls.append(
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: self.go_back())
            )

        back_btn = ft.Row(
            [
                *back_controls,
                ft.Text(display_name, size=18, weight=ft.FontWeight.BOLD),
                ft.ElevatedButton("Refresh", icon=ft.Icons.REFRESH, on_click=lambda e: self.refresh_folder_contents()),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        self.dash.folder_list.controls.append(back_btn)

        loading_indicator = ft.Row([
            ft.ProgressRing(width=20, height=20),
            ft.Text("Loading folder contents...", size=14)
        ])
        self.dash.folder_list.controls.append(loading_indicator)
        self.dash.page.update()

        try:
            result = self.dash.drive.list_files(folder_id, page_size=200, use_cache=False)
            self.dash.folder_list.controls.remove(loading_indicator)

            if result is None:
                self.dash.folder_list.controls.append(ft.Text("Network error", color=ft.Colors.ORANGE))
            else:
                files = result.get("files", [])
                if not files:
                    self.dash.folder_list.controls.append(ft.Text("Folder is empty"))
                else:
                    for f in files:
                        self.dash.folder_list.controls.append(self.dash.file_manager.create_file_item(f))
        except:
            self.dash.folder_list.controls.append(ft.Text("Error loading folder contents", color=ft.Colors.RED))

        self.dash.page.update()
    
    def refresh_folder_contents(self):
        """Force refresh of current folder view with cache invalidation.

        Invalidates DriveService cache for current folder and reloads
        contents without adding to history stack. Ensures fresh data
        from Drive API.

        Returns:
            None: Updates folder view as side effect.

        Algorithm:
            1. **Invalidate Cache**:
               a. Call dash.drive._invalidate_cache(current_folder_id)
               b. Removes cached data for current folder
               c. Forces API call on next list_files
            
            2. **Reload Contents**:
               a. Call show_folder_contents() with:
                  i. folder_id: dash.current_folder_id
                  ii. folder_name: dash.current_folder_name
                  iii. push_to_stack: False (no history entry)
               b. Reloads same folder with fresh data

        Interactions:
            - **DriveService._invalidate_cache()**: Cache management
            - **show_folder_contents()**: Reload display

        Example:
            >>> # User clicks Refresh button
            >>> navigator.refresh_folder_contents()
            >>> # Current folder reloaded with fresh data
            >>> # No duplicate in history stack
            >>> 
            >>> # After file upload
            >>> dashboard.drive.upload_file('file.pdf', current_folder_id)
            >>> navigator.refresh_folder_contents()
            >>> # Shows newly uploaded file

        See Also:
            - :meth:`show_folder_contents`: Main navigation method
            - :meth:`~services.drive_service.DriveService._invalidate_cache`: Cache management

        Notes:
            - Always gets fresh data from API
            - Does not add to history stack
            - Useful after file operations (upload, delete)
            - Called from refresh button in header
            - Maintains current folder context
        """
        self.dash.drive._invalidate_cache(self.dash.current_folder_id)
        self.show_folder_contents(self.dash.current_folder_id, self.dash.current_folder_name, push_to_stack=False)
    
    def go_back(self):
        """Navigate to previous folder using history stack.

        Pops previous context from history stack and restores that view.
        Handles both folder navigation and root-level view restoration.
        Mimics browser back button behavior.

        Returns:
            None: Restores previous view as side effect.

        Algorithm:
            1. **Check History**:
               a. If dash.folder_stack is empty:
                  i. No history to go back to
                  ii. Return early (no-op)
            
            2. **Pop Previous Context**:
               a. Pop tuple from folder_stack: (fid, fname)
               b. fid: previous folder ID
               c. fname: previous folder name
            
            3. **Restore State**:
               a. Set dash.current_folder_id = fid
               b. Set dash.current_folder_name = fname
               c. Dashboard now tracks previous folder
            
            4. **Route to Appropriate Loader**:
               a. If fid == "root":
                  i. Returning to root-level view
                  ii. Check dash.current_view to determine which root:
                      - "your_folders": Call load_your_folders()
                      - "paste_links": Call paste_links_manager.load_paste_links_view()
                      - "shared_drives": Call load_shared_drives()
               b. Else (specific folder):
                  i. Call show_folder_contents():
                     - folder_id: fid
                     - folder_name: fname
                     - push_to_stack: False (already popped)

        Interactions:
            - **Dashboard.folder_stack**: History stack (pop)
            - **load_your_folders()**: Root view loader
            - **load_shared_drives()**: Shared drives loader
            - **show_folder_contents()**: Folder loader
            - **PasteLinksManager.load_paste_links_view()**: Paste links view

        Example:
            >>> # Navigation sequence
            >>> navigator.load_your_folders()
            >>> # Stack: []
            >>> 
            >>> navigator.show_folder_contents('folder_1', 'Docs')
            >>> # Stack: [('root', 'My Drive')]
            >>> 
            >>> navigator.show_folder_contents('folder_2', 'Reports')
            >>> # Stack: [('root', 'My Drive'), ('folder_1', 'Docs')]
            >>> 
            >>> navigator.go_back()
            >>> # Returns to Docs folder
            >>> # Stack: [('root', 'My Drive')]
            >>> 
            >>> navigator.go_back()
            >>> # Returns to My Drive root
            >>> # Stack: []
            >>> 
            >>> navigator.go_back()
            >>> # No history, nothing happens
            >>> # Stack: []

        See Also:
            - :meth:`show_folder_contents`: Sets up history
            - :meth:`load_your_folders`: Root view
            - :meth:`load_shared_drives`: Shared drives view

        Notes:
            - Mimics browser back button
            - Stack stores (id, name) tuples
            - Root ID always "root"
            - Routes to correct root view based on context
            - push_to_stack=False prevents re-adding to history
            - Safe to call with empty stack (returns early)
            - Maintains proper navigation context
        """
        if not self.dash.folder_stack:
            return
        fid, fname = self.dash.folder_stack.pop()
        self.dash.current_folder_id = fid
        self.dash.current_folder_name = fname

        if fid == "root":
            if self.dash.current_view == "your_folders":
                self.load_your_folders()
            elif self.dash.current_view == "paste_links":
                self.dash.paste_links_manager.load_paste_links_view()
        else:
            self.show_folder_contents(fid, fname, push_to_stack=False)
    
    def reset_to_root(self):
        """Reset navigation to My Drive root, clearing all history.

        Clears navigation history stack and returns to My Drive root view.
        Useful for "home" button or resetting navigation state.

        Returns:
            None: Resets to root view as side effect.

        Algorithm:
            1. **Clear History**:
               a. Set dash.folder_stack = [] (empty list)
               b. Removes all back navigation
            
            2. **Reset State**:
               a. Set dash.current_folder_id = "root"
               b. Set dash.current_folder_name = "My Drive"
            
            3. **Load Root View**:
               a. Call load_your_folders()
               b. Displays My Drive root folders

        Interactions:
            - **Dashboard.folder_stack**: History clearing
            - **load_your_folders()**: Root view loader

        Example:
            >>> # User deep in folder hierarchy
            >>> # Navigation: Root → Docs → 2024 → Reports
            >>> # Stack: [('root', 'My Drive'), ('folder_1', 'Docs'), ('folder_2', '2024')]
            >>> 
            >>> # User clicks "Home" button
            >>> navigator.reset_to_root()
            >>> # Returns to My Drive root
            >>> # Stack: []
            >>> # No back navigation available

        See Also:
            - :meth:`load_your_folders`: Root view loader
            - :meth:`go_back`: Single-step back navigation

        Notes:
            - Clears entire history stack
            - Always returns to My Drive (not shared drives)
            - Useful for home button functionality
            - Cannot go back after reset
            - State fully reset to initial
        """
        self.dash.folder_stack = []
        self.dash.current_folder_id = "root"
        self.dash.current_folder_name = "My Drive"
        self.load_your_folders()
    
    def handle_search(self, e):
        """Execute search query and display results across entire Drive.

        Reads search query from Dashboard search field, executes search
        via DriveService, and displays matching files and folders.
        Empty query resets to My Drive root view.

        Args:
            e (ft.ControlEvent): Event from search field (typically submit/enter).
                Event data not used, query read from dash.search_field.value.

        Returns:
            None: Updates folder_list with search results as side effect.

        Algorithm:
            1. **Get Search Query**:
               a. Read dash.search_field.value
               b. Call .strip() to remove whitespace
               c. Store in query variable
            
            2. **Check Empty Query**:
               a. If query is empty string:
                  i. Call load_your_folders()
                  ii. Resets to root view
                  iii. Return early
            
            3. **Execute Search**:
               a. Call dash.drive.search_files(query)
               b. Searches entire Drive for matching files/folders
               c. Returns list of matching items or empty list
            
            4. **Clear UI**:
               a. Call dash.folder_list.controls.clear()
               b. Removes current view
            
            5. **Handle Results**:
               a. If results list empty:
                  i. Append message: "No results"
               b. Else for each result item:
                  i. Check mimeType:
                     - If "application/vnd.google-apps.folder":
                       - Call file_manager.create_folder_item(item, 0)
                       - Displays as folder (no subfolder count)
                     - Else (regular file):
                       - Call file_manager.create_file_item(item)
                       - Displays as file
                  ii. Append to folder_list.controls
            
            6. **Update Display**:
               a. Call dash.page.update()
               b. Shows search results

        Interactions:
            - **Dashboard.search_field**: Query input
            - **DriveService.search_files()**: Search execution
            - **FileManager.create_folder_item()**: Folder UI
            - **FileManager.create_file_item()**: File UI

        Example:
            >>> # User types "budget" and presses Enter
            >>> # Event triggers handle_search
            >>> navigator.handle_search(event)
            >>> # Dashboard shows:
            >>> # - budget_2024.xlsx (file)
            >>> # - Budget Reports/ (folder)
            >>> # - annual_budget.pdf (file)
            >>> 
            >>> # Empty search (clear/reset)
            >>> dashboard.search_field.value = "   "  # whitespace
            >>> navigator.handle_search(event)
            >>> # Returns to My Drive root view
            >>> 
            >>> # No results
            >>> dashboard.search_field.value = "xyzabc123"
            >>> navigator.handle_search(event)
            >>> # Shows: "No results"

        See Also:
            - :meth:`~services.drive_service.DriveService.search_files`: Search API
            - :meth:`load_your_folders`: Reset view
            - :meth:`~ui.dashboard_modules.file_manager.FileManager.create_file_item`: File display

        Notes:
            - Searches entire Drive (not just current folder)
            - Case-insensitive partial name matching
            - Empty query returns to root view
            - No subfolder count for result folders
            - Both files and folders in results
            - Results not cached (live search)
            - Connected to search field submit event
            - No pagination (all results shown)
        """
        query = self.dash.search_field.value.strip()
        if not query:
            self.load_your_folders()
            return
        results = self.dash.drive.search_files(query)
        self.dash.folder_list.controls.clear()
        if not results:
            self.dash.folder_list.controls.append(ft.Text("No results"))
        else:
            for r in results:
                if r.get("mimeType") == "application/vnd.google-apps.folder":
                    self.dash.folder_list.controls.append(self.dash.file_manager.create_folder_item(r, 0))
                else:
                    self.dash.folder_list.controls.append(self.dash.file_manager.create_file_item(r))
        self.dash.page.update()