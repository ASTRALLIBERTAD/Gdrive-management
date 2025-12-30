---
id: "handle_search"
sidebar_position: 10
title: "handle_search"
---

# ⚙️ handle_search

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`folder_navigator.py`](./folder_navigator.py) | **Line:** 878
:::

Execute search query and display results across entire Drive.

Reads search query from Dashboard search field, executes search
via DriveService, and displays matching files and folders.
Empty query resets to My Drive root view.

## Parameters

- **`e`** (ft.ControlEvent): Event from search field (typically submit/enter). Event data not used, query read from dash.search_field.value.

## Returns

**Type**: `None`


## Algorithm

- 1. **Get Search Query**:
    - a. Read dash.search_field.value
    - b. Call .strip() to remove whitespace
    - c. Store in query variable

  - 2. **Check Empty Query**:
    - a. If query is empty string:
    - i. Call load_your_folders()
    - ii. Resets to root view
    - iii. Return early

  - 3. **Execute Search**:
    - a. Call dash.drive.search_files(query)
    - b. Searches entire Drive for matching files/folders
    - c. Returns list of matching items or empty list

  - 4. **Clear UI**:
    - a. Call dash.folder_list.controls.clear()
    - b. Removes current view

  - 5. **Handle Results**:
    - a. If results list empty:
    - i. Append message: "No results"
    - b. Else for each result item:
    - i. Check mimeType:
    - - If "application/vnd.google-apps.folder":
    - - Call file_manager.create_folder_item(item, 0)
    - - Displays as folder (no subfolder count)
    - - Else (regular file):
    - - Call file_manager.create_file_item(item)
    - - Displays as file
    - ii. Append to folder_list.controls

  - 6. **Update Display**:
    - a. Call dash.page.update()
    - b. Shows search results

## Interactions

- **Dashboard.search_field**: Query input
- **DriveService.search_files()**: Search execution
- **FileManager.create_folder_item()**: Folder UI
- **FileManager.create_file_item()**: File UI

## Example

```python
# User types "budget" and presses Enter
# Event triggers handle_search
navigator.handle_search(event)
# Dashboard shows:
# - budget_2024.xlsx (file)
# - Budget Reports/ (folder)
# - annual_budget.pdf (file)

# Empty search (clear/reset)
dashboard.search_field.value = "   "  # whitespace
navigator.handle_search(event)
# Returns to My Drive root view

# No results
dashboard.search_field.value = "xyzabc123"
navigator.handle_search(event)
# Shows: "No results"
```

## See Also

- `search_files()`: Search API
- `load_your_folders()`: Reset view
- `create_file_item()`: File display

## Notes

- Searches entire Drive (not just current folder)
- Case-insensitive partial name matching
- Empty query returns to root view
- No subfolder count for result folders
- Both files and folders in results
- Results not cached (live search)
- Connected to search field submit event
- No pagination (all results shown)
