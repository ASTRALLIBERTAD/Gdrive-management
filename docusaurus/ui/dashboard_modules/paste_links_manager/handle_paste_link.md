---
id: "handle_paste_link"
sidebar_position: 10
title: "handle_paste_link"
---

# ⚙️ handle_paste_link

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`paste_links_manager.py`](./paste_links_manager.py) | **Line:** 909
:::

Process pasted Drive link with validation, resolution, and routing.

Validates input, resolves Drive URL to file/folder ID via API,
saves to history, and opens appropriate view (folder or preview).
Shows feedback via snackbars throughout process.

## Parameters

- **`e`** (ft.ControlEvent): Button click event from "Open Link" button. Event data not used, link read from dash.paste_link_field.value.

## Returns

**Type**: `None`


## Algorithm

- 1. **Get and Validate Input**:
    - a. Read dash.paste_link_field.value
    - b. Call .strip() to remove whitespace
    - c. Print debug message with link
    - d. If empty string:
    - i. Print debug message
    - ii. Return early (no-op)

  - 2. **Show Loading Feedback**:
    - a. Create SnackBar: "Loading Drive link..."
    - b. Set open=True
    - c. Assign to dash.page.snack_bar
    - d. Call dash.page.update() to display

  - 3. **Try Link Resolution**:
    - a. Enter try block for error handling
    - b. Call dash.drive.resolve_drive_link(link)
    - c. Returns (file_id, info) or (None, None)
    - d. Print debug message with results

  - 4. **Validate Resolution**:
    - a. If file_id is None OR info is None:
    - i. Resolution failed
    - ii. Create error snackbar:
    - - Message: "Invalid or inaccessible Drive link"
    - - bgcolor: RED_400
    - - open: True
    - iii. Assign to dash.page.snack_bar
    - iv. Call dash.page.update()
    - v. Return early

  - 5. **Extract Metadata**:
    - a. Get mime_type: info.get("mimeType", "")
    - b. Get name: info.get("name", "Shared Item")
    - c. Print debug message with details

  - 6. **Save to History** (nested try):
    - a. Enter try block
    - b. Call add_saved_link(file_id, info, link)
    - c. Returns bool: saved_added
    - d. If saved_added is True:
    - i. Create snackbar: "Saved link"
    - e. Else (already exists):
    - i. Create snackbar: "Link already saved"
    - f. Assign snackbar to dash.page.snack_bar
    - g. Catch Exception if save fails:
    - i. Print error message

  - 7. **Route by Type** - Folder:
    - a. If mime_type == "application/vnd.google-apps.folder":
    - i. Create success snackbar:
    - - Message: f"Opening folder: &#123;name&#125;"
    - - bgcolor: GREEN_400
    - ii. Assign to dash.page.snack_bar
    - iii. Call dash.page.update()
    - iv. Call folder_navigator.show_folder_contents(file_id, name)
    - v. Navigates to folder

  - 8. **Route by Type** - File (else):
    - a. Check if preview service available
    - b. If self.file_preview exists:
    - i. Create info snackbar:
    - - Message: f"Opening preview: &#123;name&#125;"
    - - bgcolor: BLUE_400
    - ii. Assign to dash.page.snack_bar
    - iii. Call dash.page.update()
    - iv. Call file_preview.show_preview(file_id, name)
    - c. Else (no preview):
    - i. Create info snackbar:
    - - Message: f"File detected: &#123;name&#125;"
    - - bgcolor: BLUE_400
    - ii. Assign to dash.page.snack_bar
    - iii. Call dash.page.update()
    - iv. Call file_manager.show_file_info(info)

  - 9. **Clear Input**:
    - a. Set dash.paste_link_field.value = "" (empty)
    - b. Clears input for next link

  - 10. **Handle Errors**:
    - a. Catch any Exception in outer try
    - b. Print error message with exception
    - c. Create error snackbar with exception message
    - d. bgcolor: RED_400
    - e. Assign to dash.page.snack_bar

  - 11. **Refresh View** (if active):
    - a. Check if dash.current_view == "paste_links"
    - b. If yes:
    - i. Call load_paste_links_view()
    - ii. Refreshes to show new saved link

  - 12. **Final Update**:
    - a. Call dash.page.update()
    - b. Ensures all changes rendered

## Interactions

- **Dashboard.paste_link_field**: Input control
- **DriveService.resolve_drive_link()**: URL resolution
- **add_saved_link()**: History persistence
- **FolderNavigator.show_folder_contents()**: Folder navigation
- **FilePreviewService.show_preview()**: File preview
- **FileManager.show_file_info()**: Info fallback
- **ft.SnackBar**: User feedback

## Example

```python
# Valid folder link
dashboard.paste_link_field.value = "https://drive.google.com/drive/folders/abc123"
paste_manager.handle_paste_link(event)
# Shows: "Loading Drive link..."
# Shows: "Saved link"
# Shows: "Opening folder: Project Files"
# Navigates to folder

# Valid file link (preview available)
dashboard.paste_link_field.value = "https://drive.google.com/file/d/xyz789/view"
paste_manager.handle_paste_link(event)
# Shows: "Opening preview: Document.pdf"
# Opens preview modal

# Invalid link
dashboard.paste_link_field.value = "https://invalid-url.com"
paste_manager.handle_paste_link(event)
# Shows: "Invalid or inaccessible Drive link"

# Already saved link
dashboard.paste_link_field.value = "https://drive.google.com/drive/folders/abc123"
paste_manager.handle_paste_link(event)
# Shows: "Link already saved"
# Still opens folder
```

## See Also

- `resolve_drive_link()`: URL parsing
- `add_saved_link()`: History persistence
- `load_paste_links_view()`: View refresh

## Notes

- Multiple snackbar feedback points
- Debug prints throughout (development aid)
- Graceful error handling at multiple levels
- Input cleared on success
- View refreshed if currently active
- Preview or info fallback for files
- Duplicate detection during save
- Empty input returns early (silent)
