---
id: "pastelinksmanager"
sidebar_position: 2
title: "PasteLinksManager"
---

# 📦 PasteLinksManager

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Completeness](https://img.shields.io/badge/Docs-20%25-red)

:::info Source
**File:** [`paste_links_manager.py`](./paste_links_manager.py) | **Line:** 24
:::

Drive link paste and management system with persistent history.

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

## Purpose

- Parse and resolve Google Drive URLs to file/folder IDs
        - Validate Drive link accessibility via API
        - Save validated links to persistent JSON storage
        - Load and display saved links history
        - Provide UI for link input and management
        - Navigate to folders or preview files from links
        - Delete saved links from history
        - Handle multiple Drive URL formats

## Attributes

- **`dash`** (Dashboard): Reference to parent Dashboard instance. Provides access to page, drive service, folder_navigator, file_manager, paste_link_field input control, and current_view state tracking.
- **`file_preview`** (FilePreviewService or None): Service for displaying file previews. Handles images, text, PDFs, Office docs. None if service import fails (graceful degradation with fallback to file info).

## Interactions

- **Dashboard**: Parent container managing state and UI
- **DriveService**: Resolves links and fetches metadata (via dash.drive)
- **FilePreviewService**: Displays file previews in modal
- **FolderNavigator**: Navigates to folders (via dash.folder_navigator)
- **FileManager**: Shows file info fallback (via dash.file_manager)
- **JSON file**: Persistent storage (saved_links.json)
- **ft.TextField**: Link input field (dash.paste_link_field)
- **ft.SnackBar**: User feedback messages
- Algorithm (High-Level Workflow):
- *Phase 1: Initialization**
- 1. Store Dashboard reference
- 2. Import FilePreviewService (graceful failure)
- 3. Initialize preview service with page and drive
- 4. Ready to manage links
- *Phase 2: View Loading** (load_paste_links_view)
- 1. Set current_view = "paste_links"
- 2. Clear folder_list UI
- 3. Build header section
- 4. Build paste section:
- a. Input field for URL
- b. "Open Link" button
- c. Help text with format examples
- 5. Build saved links section:
- a. "Saved Links" header
- b. List of saved link items (cards)
- 6. Update page to display
- *Phase 3: Link Pasting** (handle_paste_link)
- 1. User pastes Drive URL and clicks "Open Link"
- 2. Validate non-empty input
- 3. Show "Loading..." snackbar
- 4. Resolve link via drive.resolve_drive_link():
- a. Extract file/folder ID from URL
- b. Fetch metadata from Drive API
- c. Return (file_id, info) or (None, None)
- 5. If invalid:
- a. Show error snackbar
- b. Return early
- 6. If valid:
- a. Save to history (add_saved_link)
- b. Show success/already-saved snackbar
- c. Route based on type:
- Folder → Navigate via folder_navigator
- File → Preview or show info
- 7. Clear input field
- 8. Refresh view if still active
- *Phase 4: Saved Link Management**
- 1. Load saved links from JSON file
- 2. Check for duplicates (by ID)
- 3. Add new link to list
- 4. Save updated list to JSON
- 5. Display in UI as clickable cards
- *Phase 5: Link Opening** (open_saved_link)
- 1. User clicks saved link card
- 2. Check MIME type:
- a. Folder → Navigate to contents
- b. File → Preview or show info
- 3. Update UI accordingly
- *Phase 6: Link Deletion** (delete_saved_link)
- 1. User clicks delete button on card
- 2. Load current links
- 3. Filter out deleted item
- 4. Save updated list
- 5. Refresh view if active

## Example

```python
# Initialize in Dashboard
from ui.dashboard_modules.paste_links_manager import PasteLinksManager
paste_manager = PasteLinksManager(dashboard)

# Load paste links view
paste_manager.load_paste_links_view()
# Shows input field and saved links

# User pastes folder link
dashboard.paste_link_field.value = "https://drive.google.com/drive/folders/abc123"
paste_manager.handle_paste_link(event)
# Resolves link → Saves to history → Navigates to folder

# User pastes file link
dashboard.paste_link_field.value = "https://drive.google.com/file/d/xyz789/view"
paste_manager.handle_paste_link(event)
# Resolves link → Saves to history → Opens preview

# Access saved link
saved_links = paste_manager.load_saved_links()
print(saved_links)
[
    {'id': 'abc123', 'name': 'Shared Folder', 'mimeType': '...folder', 'url': '...'},
    {'id': 'xyz789', 'name': 'Document.pdf', 'mimeType': 'application/pdf', 'url': '...'}
    ]

# Open saved link
paste_manager.open_saved_link(saved_links[0])
# Navigates to folder

# Delete saved link
paste_manager.delete_saved_link(saved_links[1])
# Removes from history and refreshes view
```

## See Also

- `Dashboard`: Parent container
- `DriveService`: Link resolution
- `FilePreviewService`: File preview
- `FolderNavigator`: Folder navigation
- `FileManager`: File info fallback

## Notes

- Saved links persist in saved_links.json
- Supports multiple Drive URL formats
- Duplicate detection by file ID
- Graceful degradation without preview service
- JSON file created automatically if missing
- View refreshes after link operations
- Snackbar feedback for all operations
- Click card to open, click delete icon to remove

## References

- Google Drive URLs: [https://developers.google.com/drive/api/v3/manage-sharing](https://developers.google.com/drive/api/v3/manage-sharing)
- JSON Storage: [https://docs.python.org/3/library/json.html](https://docs.python.org/3/library/json.html)
