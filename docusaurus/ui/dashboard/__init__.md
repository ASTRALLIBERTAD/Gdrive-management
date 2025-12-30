---
id: "__init__"
sidebar_position: 3
title: "__init__"
---

# 🔧 __init__

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`dashboard.py`](./dashboard.py) | **Line:** 202
:::

Initialize the Dashboard with authentication and layout setup.

Constructs the main dashboard by setting up Google Drive integration,
initializing manager modules, creating UI components, and loading the
default folder view. Establishes the foundation for all dashboard
functionality including file management, navigation, and responsive layout.

## Parameters

- **`page`** (ft.Page): Flet page instance providing UI rendering context, window dimensions, overlay system, and event handling. Must be a valid, initialized Flet page object.
- **`auth_service`** (GoogleAuth): Authentication service managing OAuth2 credentials, user session, and Drive API access. Must be authenticated before Dashboard initialization.
- **`on_logout`** (Callable): Callback function with no parameters, invoked when user clicks logout button. Typically handles cleanup and navigation to login screen. Signature: () -> None.

## Algorithm

- 1. **Store Core References**:
    - a. Assign page parameter to self.page
    - b. Assign auth_service to self.auth
    - c. Assign on_logout callback to self.on_logout

  - 2. **Initialize Drive Service**:
    - a. Call auth_service.get_service() to obtain Drive API service
    - b. Pass service to DriveService constructor
    - c. Store DriveService instance in self.drive

  - 3. **Setup Navigation State**:
    - a. Set self.current_folder_id to "root" (Drive root folder)
    - b. Set self.current_folder_name to "My Drive"
    - c. Initialize self.folder_stack as empty list []
    - d. Set self.current_view to "your_folders" (default view)

  - 4. **Retrieve User Information**:
    - a. Call auth.get_user_info() to get user profile data
    - b. Extract emailAddress from user_info dictionary
    - c. Store in self.user_email (default to "User" if unavailable)

  - 5. **Instantiate Manager Modules**:
    - a. Create FileManager instance: FileManager(self)
    - - Passes self reference for access to page, drive, etc.
    - b. Create FolderNavigator instance: FolderNavigator(self)
    - - Handles navigation and folder content display
    - c. Create PasteLinksManager instance: PasteLinksManager(self)
    - - Processes shared Drive links

  - 6. **Create Search Field Component**:
    - a. Instantiate ft.TextField with hint_text "Search"
    - b. Set prefix_icon to ft.Icons.SEARCH (magnifying glass)
    - c. Bind on_submit event to folder_navigator.handle_search
    - d. Configure styling: border_color, filled=True, expand=True
    - e. Store in self.search_field

  - 7. **Initialize Menu State**:
    - a. Set self.menu_open to False (sidebar hidden on mobile initially)

  - 8. **Create Paste Link Field Component**:
    - a. Instantiate ft.TextField with paste instruction hint text
    - b. Bind on_submit to paste_links_manager.handle_paste_link
    - c. Configure styling: expand=True, blue border colors
    - d. Store in self.paste_link_field

  - 9. **Create Folder List Container**:
    - a. Instantiate ft.Column with spacing=0
    - b. Set scroll mode to ALWAYS for scrollable content
    - c. Set expand=True to fill available vertical space
    - d. Store in self.folder_list

  - 10. **Register Resize Handler**:
    - a. Bind self.on_resize to page.on_resize event
    - b. Enables responsive sidebar visibility on window resize

  - 11. **Configure Page Properties**:
    - a. Set page.title to "Drive Manager"
    - b. Set vertical_alignment to MainAxisAlignment.START
    - c. Set horizontal_alignment to CrossAxisAlignment.STRETCH

  - 12. **Load Initial View**:
    - a. Call folder_navigator.load_your_folders()
    - b. Displays root folder contents in folder_list
    - c. Dashboard now ready for user interaction

## Interactions

- **GoogleAuth**: Retrieves Drive API service and user information
- **DriveService**: Initialized with Drive API service for file ops
- **FileManager**: Instantiated with dashboard reference
- **FolderNavigator**: Instantiated and called to load initial view
- **PasteLinksManager**: Instantiated with dashboard reference
- **ft.Page**: Configured with title, alignment, and resize handler

## Example

```python
# Create dashboard after user authentication
auth = GoogleAuth()
auth.authenticate()  # User logs in via OAuth2

def handle_logout():
    page.clean()
    show_login_screen()

dashboard = Dashboard(page, auth, handle_logout)
# Dashboard now displays root folder contents

# Access dashboard components
print(dashboard.user_email)
# user@example.com
print(dashboard.current_folder_name)
# My Drive
print(len(dashboard.folder_stack))
# 0
```

## See Also

- `GoogleAuth`: Authentication service
- `DriveService`: Drive API wrapper
- `FileManager`: File operations
- `FolderNavigator`: Navigation
- `get_view()`: Builds and returns dashboard layout

## Notes

- Auth service must be authenticated before initialization
- Initial view loads "root" folder (My Drive) automatically
- Sidebar visibility initially based on window width
- Manager modules receive self reference for accessing dashboard state
- Page resize handler registered for responsive behavior
- User email extracted safely with fallback to "User"
