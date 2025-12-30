---
id: "select_file_to_upload"
sidebar_position: 15
title: "select_file_to_upload"
---

# ⚙️ select_file_to_upload

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`file_manager.py`](./file_manager.py) | **Line:** 1514
:::

Open system file picker for uploading files to Drive.

Displays native OS file selection dialog. User can select one or
multiple files. All selected files uploaded to current Drive folder
and Dashboard refreshed to show new files.

## Returns

**Type**: `None`


## Algorithm

- 1. **Define Result Handler**:
    - a. Check if files selected:
    - i. If e.files is empty or None:
    - - Return early (user cancelled)
    - b. Upload each file:
    - i. For each file in e.files:
    - - Get file path: f.path
    - - Call dash.drive.upload_file():
    - - file_path: f.path (local path)
    - - parent_id: dash.current_folder_id
    - - Upload blocks until complete
    - c. Refresh Dashboard:
    - i. Call dash.refresh_folder_contents()
    - ii. Shows newly uploaded files

  - 2. **Create File Picker**:
    - a. Instantiate ft.FilePicker with:
    - i. on_result: result handler function
    - b. Picker tied to handler

  - 3. **Register and Show**:
    - a. Append picker to dash.page.overlay
    - b. Call dash.page.update() (makes picker available)
    - c. Call file_picker.pick_files()
    - i. Opens native file dialog
    - ii. User selects files
    - iii. Dialog closes
    - iv. Result handler called with selection

## Interactions

- **ft.FilePicker**: System file selection dialog
- **DriveService.upload_file()**: Upload operation
- **Dashboard.refresh_folder_contents()**: UI refresh
- **Dashboard.current_folder_id**: Upload destination
- **dash.page.overlay**: Picker registration

## Example

```python
# User clicks "Upload" button
file_manager.select_file_to_upload()
# Native file picker opens

# User selects single file
# → Result: [FilePickerFile(path='C:/docs/report.pdf')]
# → Upload: upload_file('C:/docs/report.pdf', current_folder_id)
# → Refresh: Dashboard shows new file

# User selects multiple files
# → Result: [file1, file2, file3]
# → Uploads all files sequentially
# → Refresh once after all complete

# User cancels
# → Result: e.files = None or []
# → Early return, no uploads
```

## See Also

- `upload_file()`: Upload method
- `refresh_folder_contents()`: Refresh
- `ft.FilePicker`: Flet file picker control

## Notes

- Uses native OS file picker
- Supports multiple file selection
- Uploads to current folder
- Sequential upload (one at a time)
- Refresh after all uploads complete
- Cancel safe (early return)
- Files must be readable
- Large files may take time
- No progress indicator during upload
- Picker must be in overlay to work
