---
id: "get_view"
sidebar_position: 12
title: "get_view"
---

# ⚙️ get_view

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`dashboard.py`](./dashboard.py) | **Line:** 1006
:::

Build and return the complete dashboard layout.

Constructs the full dashboard user interface including sidebar,
top bar with search, tab navigation, and main content area.
Assembles all components into a responsive layout that adapts
to different screen sizes.

## Returns

**Type**: `ft.Row`

                Structure: Row[sidebar_container, VerticalDivider, main_content]
                where main_content is Column[top_bar, tabs, folder_list].
                Component expands to fill available space with expand=True.

## Algorithm

- 1. **Create Sidebar Container**:
    - a. Instantiate ft.Container with fixed width=170px
    - b. Set bgcolor to light grey (ft.Colors.GREY_100)
    - c. Add padding=20 for internal spacing
    - d. Calculate visibility:
    - i. visible = (page.width &gt;= 900) OR menu_open
    - ii. Shows on desktop or when toggled on mobile
    - e. Create Column content with four buttons:
    - i. ButtonWithMenu: "+ NEW" with dropdown menu
    - - Menu items: ["Create Folder", "Upload File"]
    - - on_menu_select: self.handle_action
    - ii. ElevatedButton: "SETTINGS" (no-op currently)
    - iii. ElevatedButton: "TO-DO" with self.show_todo_view
    - iv. ElevatedButton: "ACCOUNT" with self.handle_logout
    - f. Set button spacing=15 in Column
    - g. Store in self.sidebar_container

  - 2. **Create Top Bar**:
    - a. Instantiate ft.Container with padding=20
    - b. Create Row content with three elements:
    - i. IconButton: hamburger menu (ft.Icons.MENU)
    - - on_click: self.toggle_menu
    - - visible: True (always shown)
    - ii. self.search_field: search TextField (expands)
    - iii. IconButton: account circle (ft.Icons.ACCOUNT_CIRCLE)
    - - icon_size: 36
    - - tooltip: self.user_email
    - c. Set Row alignment to SPACE_BETWEEN
    - d. Store in top_bar variable

  - 3. **Create Tab Navigation**:
    - a. Instantiate ft.Container with padding=10
    - b. Create Row content with three tab buttons:
    - i. ElevatedButton: "YOUR FOLDERS"
    - - on_click: folder_navigator.reset_to_root()
    - ii. ElevatedButton: "PASTE LINKS"
    - - on_click: paste_links_manager.load_paste_links_view()
    - iii. ElevatedButton: "SHARED DRIVES"
    - - on_click: folder_navigator.load_shared_drives()
    - c. Set Row spacing=10, alignment=CENTER
    - d. Store in tabs variable

  - 4. **Create Main Content Area**:
    - a. Instantiate ft.Column with three components:
    - i. top_bar: search and account controls
    - ii. tabs: view switching buttons
    - iii. Container with folder_list (expand=True)
    - b. Set Column expand=True to fill vertical space
    - c. Store in main_content variable

  - 5. **Assemble Final Layout**:
    - a. Create ft.Row with three components:
    - i. self.sidebar_container: navigation sidebar
    - ii. ft.VerticalDivider(width=1): separator line
    - iii. main_content: main display area
    - b. Set Row expand=True to fill available space
    - c. Return assembled Row component

## Interactions

- **ButtonWithMenu**: Custom dropdown for action menu
- **FileManager**: Handles menu action selections
- **FolderNavigator**: Handles tab navigation and search
- **PasteLinksManager**: Handles paste links view
- **TodoView**: Loaded when TO-DO button clicked

## Example

```python
# Initialize dashboard
dashboard = Dashboard(page, auth, logout_handler)

# Get complete layout
layout = dashboard.get_view()
print(type(layout))
# <class 'flet.Row'>

# Add to page for rendering
page.add(layout)
page.update()
# Full dashboard now visible with all components
```

## See Also

- `__init__()`: Initializes components used in layout
- `ButtonWithMenu`: Dropdown button
- `show_todo_view()`: TO-DO button click handler
- `handle_logout()`: ACCOUNT button click handler
- `handle_action()`: Menu selection handler

## Notes

- Layout is responsive with 900px breakpoint
- Sidebar hides on mobile, toggled by hamburger menu
- Tab buttons switch between different view modes
- Search field expands to fill available width
- folder_list populated dynamically based on view
- VerticalDivider provides visual separation
- All components configured before return
- expand=True ensures full viewport usage
