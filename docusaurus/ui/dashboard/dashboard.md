---
id: "dashboard"
sidebar_position: 2
title: "Dashboard"
---

# 📦 Dashboard

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Completeness](https://img.shields.io/badge/Docs-20%25-red)

:::info Source
**File:** [`dashboard.py`](./dashboard.py) | **Line:** 27
:::

Main application dashboard with Google Drive integration and file management.

The Dashboard class serves as the central hub of the Learning Management System,
providing a unified interface for Google Drive file operations, folder navigation,
assignment management (to-do), and link-based access to shared resources. It
orchestrates multiple specialized manager modules and handles responsive layout
adjustments for various screen sizes.
This class acts as the coordinator between the UI layer and backend services,
managing the overall application state including current folder context, view
modes (folders vs to-do), and user session information. It implements a sidebar
navigation system with context-aware content display and supports both direct
Drive folder browsing and paste-link-based access.

## Purpose

- Provide main dashboard interface for LMS file management
        - Integrate Google Drive operations with user-friendly UI
        - Coordinate between file management, navigation, and assignment modules
        - Handle responsive layout for desktop and mobile viewports
        - Manage application view states (folder view, to-do view, paste links)
        - Support both authenticated Drive access and link-based sharing

## Attributes

- **`page`** (ft.Page): Flet page instance for UI rendering and event handling. Provides access to window dimensions, overlay system, and update mechanism.
- **`auth`** (GoogleAuth): Authentication service managing OAuth2 credentials and user session. Provides access to Drive API service and user info.
- **`on_logout`** (Callable): Callback function invoked when user logs out. Typically returns user to login screen or clears session data.
- **`drive`** (DriveService): Google Drive service wrapper providing high-level API methods for file/folder operations, metadata queries, and permissions.
- **`current_folder_id`** (str): Google Drive ID of currently displayed folder. Default is "root" representing user's My Drive root folder.
- **`current_folder_name`** (str): Display name of currently active folder. Used in breadcrumb navigation and title displays. Default "My Drive".
- **`folder_stack`** (list): Navigation history stack storing folder IDs for back navigation. Enables breadcrumb trail and "go up" functionality.
- **`current_view`** (str): Active view mode identifier. Values: "your_folders" (default Drive view), "todo" (assignment management), "paste_links" (link-based access), "shared_drives" (team drive view).
- **`user_email`** (str): Email address of authenticated user. Retrieved from auth service user info. Displayed in account tooltip. Default "User".
- **`file_manager`** (FileManager): Module handling file operations including upload, download, delete, rename, and folder creation. Manages file picker dialogs and progress indicators.
- **`folder_navigator`** (FolderNavigator): Module managing folder traversal, search functionality, and view switching between folder types. Handles breadcrumb generation and folder content loading.
- **`paste_links_manager`** (PasteLinksManager): Module processing Google Drive share links, extracting file/folder IDs, and displaying linked content without requiring direct Drive permissions.
- **`search_field`** (ft.TextField): Search input component with magnifying glass icon. Triggers folder_navigator.handle_search on submit (Enter key).
- **`menu_open`** (bool): Sidebar visibility state for mobile/tablet viewports. Toggled by hamburger menu button. Always visible on desktop (>900px).
- **`paste_link_field`** (ft.TextField): Input field for pasting Google Drive share links. Processes links on Enter key via paste_links_manager.
- **`folder_list`** (ft.Column): Main content container displaying folder contents, search results, or to-do view. Scrollable with dynamic content updates.

## Interactions

- **GoogleAuth**: Authenticates user and provides Drive API service
- **DriveService**: Wraps Google Drive API for file/folder operations
- **FileManager**: Handles file uploads, downloads, and folder creation
- **FolderNavigator**: Manages navigation, search, and folder content display
- **PasteLinksManager**: Processes shared Drive links and displays content
- **TodoView**: Assignment management interface accessible from sidebar
- **ButtonWithMenu**: Custom dropdown button component for action menu
- **ft.Page**: Flet page for UI updates and responsive layout handling
- Algorithm (High-Level Workflow):
- *Phase 1: Initialization**
- 1. Store references to page, auth service, and logout callback
- 2. Create DriveService instance from auth.get_service()
- 3. Initialize folder navigation state (root folder, empty stack)
- 4. Set default view mode to "your_folders"
- 5. Retrieve user email from auth service for display
- 6. Instantiate manager modules (FileManager, FolderNavigator, PasteLinksManager)
- 7. Create search field with submit handler
- 8. Create paste link field for shared link processing
- 9. Create scrollable folder list container
- 10. Register resize event handler for responsive layout
- 11. Set page title and alignment properties
- 12. Trigger initial folder load (your_folders view)
- *Phase 2: View Management**
- 1. Monitor current_view state variable
- 2. When view changes:
- a. Clear folder_list contents
- b. If "your_folders": load Drive root folder contents
- c. If "todo": instantiate TodoView and display
- d. If "paste_links": show paste link input interface
- e. If "shared_drives": load team drives list
- 3. Update page to render new view
- *Phase 3: Responsive Layout Handling**
- 1. Listen for window resize events via page.on_resize
- 2. Check page.width against breakpoints
- 3. If width &gt;= 900px (desktop):
- a. Show sidebar permanently
- b. Set menu_open to False (disable toggle state)
- 4. If width < 900px (mobile/tablet):
- a. Show sidebar only if menu_open is True
- b. Enable hamburger menu toggle functionality
- 5. Update page to apply visibility changes
- *Phase 4: Navigation Flow**
- 1. User clicks folder in folder_list
- 2. Delegate to folder_navigator.show_folder_contents()
- 3. Push current folder to folder_stack for back navigation
- 4. Update current_folder_id and current_folder_name
- 5. Load and display new folder contents
- 6. Update breadcrumb trail in UI
- *Phase 5: Action Handling**
- 1. User clicks action button (+ NEW, TO-DO, SETTINGS, etc.)
- 2. Route to appropriate handler method
- 3. For file operations: delegate to file_manager
- 4. For navigation: delegate to folder_navigator
- 5. For view switches: update current_view and rebuild UI
- 6. Update page to reflect changes

## Example

```python
# Initialize dashboard with auth service
from services.google_auth import GoogleAuth
auth = GoogleAuth()
def logout_handler():
    print("User logged out")

dashboard = Dashboard(page, auth, logout_handler)

# Dashboard automatically loads root folder
print(f"Current folder: {dashboard.current_folder_name}")
# Current folder: My Drive

# User navigates to subfolder
dashboard.show_folder_contents('folder_abc123', 'Documents')
print(f"Current folder: {dashboard.current_folder_name}")
# Current folder: Documents

# User switches to to-do view
dashboard.show_todo_view(None)
print(f"Current view: {dashboard.current_view}")
# Current view: todo

# Get dashboard layout for rendering
layout = dashboard.get_view()
page.add(layout)
```

## See Also

- `DriveService`: Google Drive API wrapper
- `GoogleAuth`: Authentication service
- `TodoView`: Assignment management interface
- `FileManager`: File operations
- `FolderNavigator`: Navigation
- `PasteLinksManager`: Link handling
- `ButtonWithMenu`: Dropdown button
- `flet`: Flet UI framework documentation

## Notes

- Sidebar automatically hides on mobile (&lt;900px width) with toggle button
- All file operations delegated to specialized manager modules
- View state persists until explicitly changed by user action
- Folder navigation maintains history stack for back button functionality
- User email displayed in account icon tooltip for easy identification
- Search functionality scans current folder and subfolders recursively
- Paste links allow access without direct Drive permissions

## References

- Google Drive API v3: [https://developers.google.com/drive/api/v3/reference](https://developers.google.com/drive/api/v3/reference)
- Flet Framework: [https://flet.dev/docs/](https://flet.dev/docs/)
- Material Design Icons: [https://fonts.google.com/icons](https://fonts.google.com/icons)
