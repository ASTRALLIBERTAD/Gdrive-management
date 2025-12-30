---
id: "build_saved_links_ui"
sidebar_position: 11
title: "build_saved_links_ui"
---

# ⚙️ build_saved_links_ui

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`paste_links_manager.py`](./paste_links_manager.py) | **Line:** 1125
:::

Construct UI for saved links list with clickable cards.

Generates Column containing visual cards for each saved link,
with icon, name, action buttons (preview/open, delete). Returns
empty state message if no saved links.

## Returns

**Type**: `ft.Column`

                Each card is Container with Row of Icon, Text, IconButtons.
                Spacing: 4px between cards.

## Algorithm

- 1. **Load Saved Links**:
    - a. Call self.load_saved_links()
    - b. Returns list of saved link dicts

  - 2. **Create Column**:
    - a. Instantiate ft.Column with spacing=4
    - b. Store in col variable

  - 3. **Check Empty State**:
    - a. If saved list is empty:
    - i. Append Text: "No saved links yet." (grey color)
    - ii. Return col (early return)

  - 4. **Iterate Saved Links**:
    - a. For each item in saved:
    - i. Determine item type:
    - - is_folder = (mimeType == "application/vnd.google-apps.folder")
    - ii. Select icon:
    - - If is_folder: icon = FOLDER
    - - Else: icon = DESCRIPTION

  - 5. **Build Link Card** (for each item):
    - a. Create ft.Row with:
    - i. ft.Icon(icon, size=20)
    - ii. ft.Text(item["name"], expand=True)
    - iii. Preview/Open IconButton:
    - - icon: VISIBILITY
    - - tooltip: "Preview" or "Open" based on type
    - - on_click: lambda calls open_saved_link(item)
    - - Only if preview available OR is folder
    - - Else: empty Container
    - iv. Delete IconButton:
    - - icon: DELETE
    - - tooltip: "Delete"
    - - on_click: lambda calls delete_saved_link(item)

    - b. Wrap Row in ft.Container with:
    - i. content: Row
    - ii. padding: 8px
    - iii. ink: True (ripple effect)
    - iv. on_click: lambda calls open_saved_link(item)
    - v. border: 1px grey border all sides
    - vi. border_radius: 8px (rounded)

    - c. Append container to col.controls

  - 6. **Return Column**:
    - a. Return col with all link cards

## Interactions

- **load_saved_links()**: Retrieves link data
- **open_saved_link()**: Click handler
- **delete_saved_link()**: Delete handler
- **ft.Column, ft.Row, ft.Container**: Layout
- **ft.Icon, ft.Text, ft.IconButton**: UI elements

## Example

```python
# Build saved links UI
ui = paste_manager.build_saved_links_ui()
# Returns Column with cards:
# ┌────────────────────────────────┐
# │ 📁 Project Folder    [👁][🗑] │
# │ 📄 Document.pdf      [👁][🗑] │
# │ 📁 Shared Resources  [👁][🗑] │
# └────────────────────────────────┘

# No saved links
ui = paste_manager.build_saved_links_ui()
# Returns: "No saved links yet."
```

## See Also

- `load_saved_links()`: Data source
- `open_saved_link()`: Click handler
- `delete_saved_link()`: Delete handler
- `load_paste_links_view()`: Uses this UI

## Notes

- Empty state friendly message
- Icon varies by type (folder/file)
- Preview button conditional (service + file)
- Delete button always present
- Card clickable (opens link)
- Ripple effect on click (ink=True)
- Rounded borders (8px radius)
- Lambda captures item for handlers
- Spacing 4px between cards
