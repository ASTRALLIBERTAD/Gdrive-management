---
id: "load_paste_links_view"
sidebar_position: 9
title: "load_paste_links_view"
---

# ⚙️ load_paste_links_view

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`paste_links_manager.py`](./paste_links_manager.py) | **Line:** 751
:::

Render Paste Drive Links view with input and saved history.

Builds and displays complete paste links interface including header,
input section with help text, and saved links list. Clears previous
view and updates Dashboard state.

## Returns

**Type**: `None`


## Algorithm

- 1. **Set View State**:
    - a. Set dash.current_view = "paste_links"
    - b. Tracks active view for refresh logic

  - 2. **Clear UI**:
    - a. Call dash.folder_list.controls.clear()
    - b. Removes all previous content

  - 3. **Build Header Section**:
    - a. Create ft.Container with:
    - i. Text: "Paste Drive Links" (size 20, bold)
    - ii. padding: 10px
    - b. Store in header variable

  - 4. **Build Paste Section**:
    - a. Create ft.Container with:
    - i. Column containing:
    - - Instruction text (size 14)
    - - paste_link_field (TextField reference)
    - - "Open Link" button:
    - - on_click: handle_paste_link
    - - bgcolor: BLUE_400
    - - color: WHITE
    - - icon: LINK
    - - Help text showing supported formats:
    - - Folder format
    - - File format
    - - Query parameter format
    - - size 12, grey color
    - ii. spacing: 10px between elements
    - iii. padding: 20px
    - iv. bgcolor: BLUE_50 (light blue background)
    - v. border_radius: 10px (rounded corners)
    - b. Store in paste_section variable

  - 5. **Build Saved Links Header**:
    - a. Create ft.Container with:
    - i. Text: "Saved Links" (size 16, bold)
    - ii. padding: top=20, bottom=10, left=10
    - b. Store in saved_links_header variable

  - 6. **Build Saved Links List**:
    - a. Call self.build_saved_links_ui()
    - b. Returns Column with link cards
    - c. Wrap in ft.Container with padding: 10px
    - d. Store in saved_links_list variable

  - 7. **Assemble View**:
    - a. Call dash.folder_list.controls.extend() with list:
    - i. header
    - ii. paste_section
    - iii. saved_links_header
    - iv. saved_links_list
    - b. Adds all sections to display

  - 8. **Update Display**:
    - a. Call dash.page.update()
    - b. Renders complete view

## Interactions

- **Dashboard.folder_list**: Main display area
- **Dashboard.paste_link_field**: Input control
- **build_saved_links_ui()**: Saved links section
- **ft.Container, ft.Column, ft.Text**: UI components

## Example

```python
# Load paste links view
paste_manager.load_paste_links_view()
# Dashboard shows:
# ┌─ Paste Drive Links ─────────────┐
# │ Paste a Google Drive link:      │
# │ [_________________________]      │
# │ [Open Link 🔗]                   │
# │ Supported formats:               │
# │ • folders/FOLDER_ID             │
# │ • file/d/FILE_ID                │
# │ • ...?id=ID                     │
# ├─ Saved Links ───────────────────┤
# │ 📁 Project Folder    [👁][🗑]   │
# │ 📄 Document.pdf      [👁][🗑]   │
# └─────────────────────────────────┘
```

## See Also

- `handle_paste_link()`: Input handler
- `build_saved_links_ui()`: Saved links display
- `delete_saved_link()`: Refreshes this view

## Notes

- Full view replacement (clears previous)
- Input field referenced from Dashboard
- Help text with format examples
- Blue theme for paste section
- Saved links section separate
- Called on view switch and refresh
