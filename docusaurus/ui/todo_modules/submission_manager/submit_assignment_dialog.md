---
id: "submit_assignment_dialog"
sidebar_position: 5
title: "submit_assignment_dialog"
---

# ⚙️ submit_assignment_dialog

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`submission_manager.py`](./submission_manager.py) | **Line:** 409
:::

Display student submission dialog for uploading assignment work.

Creates an interactive modal dialog allowing students to submit their
assignment by uploading a file to Google Drive, optionally adding
submission notes, and selecting a target folder. Handles the complete
submission workflow including validation, file upload, record creation,
and user feedback.

## Parameters

- **`assignment`** (dict): Assignment dictionary containing: - id (str): Unique assignment identifier - title (str): Assignment title/name - subject (str): Subject/category (e.g., 'Math', 'Science') - drive_folder_id (str): Target Google Drive folder ID for uploads - deadline (str): ISO 8601 deadline timestamp

## Returns

**Type**: `None`

                Updates UI and data stores as side effects.

## Exceptions

No direct exceptions raised. All errors handled gracefully with:
            - Snackbar notifications for user feedback
            - Status text updates within dialog
            - Early return for validation failures

## Algorithm

- 1. **Prerequisites Validation**:
    - a. Extract subject from assignment dictionary (default to 'Other')
    - b. Extract drive_folder_id from assignment dictionary
    - c. Check if self.todo.drive_service is available and authenticated
    - d. If drive_service is None:
    - - Show error snackbar "No Drive service available"
    - - Return immediately (abort dialog creation)
    - e. Check if drive_folder_id exists and is not empty
    - f. If drive_folder_id missing:
    - - Show error snackbar "No submission folder linked"
    - - Return immediately (abort dialog creation)

  - 2. **UI Component Initialization**:
    - a. Create selected_folder_id list with drive_folder_id as default
    - b. Retrieve folder name using get_folder_name_by_id()
    - c. Create folder_display text showing "Upload to: &#123;folder_name&#125;"
    - d. Create submission_text TextField for student notes (multiline, 3+ lines)
    - e. Create upload_status Text element (initially empty string)
    - f. Set up folder browser button with "Browse Folders" label

  - 3. **Folder Browser Setup**:
    - a. Define update_selected_folder(fid) callback function
    - b. Callback updates selected_folder_id[0] with new folder ID
    - c. Callback retrieves new folder name using get_folder_name_by_id()
    - d. If folder name is "Linked Folder", query Drive service for actual name
    - e. Update folder_display.value with new folder name
    - f. Call page.update() to refresh UI
    - g. Connect callback to change_folder_btn click event
    - h. Callback invokes storage_manager.create_browse_dialog()

  - 4. **File Picker Handler Definition** (on_file_picked):
    - a. Check if files were selected in picker (e.files not empty)
    - b. If no files, return immediately (user cancelled)
    - c. Extract file_path from e.files[0].path
    - d. Extract file_name from e.files[0].name
    - e. Get student identifier from current_student_email (split by '@')
    - f. Update upload_status to "Uploading &#123;file_name&#125;..."
    - g. Call page.update() to show upload status
    - h. Enter try-except block for upload operation

  - 5. **File Upload Process** (within on_file_picked):
    - a. Call storage_manager.upload_submission_to_link_drive() with:
    - - file_path: full path to local file
    - - file_name: original file name
    - - subject: assignment subject for folder organization
    - - student_name: student identifier from email
    - - folder_id: selected_folder_id[0]
    - b. Store upload result (file metadata from Drive API)
    - c. If result is truthy (upload succeeded):
    - - Update upload_status to "✓ Uploaded to link drive"
    - - Show success snackbar "File uploaded to link drive folder!"
    - d. If result is falsy (upload failed):
    - - Update upload_status to "✗ Upload failed"
    - - Show error snackbar "Upload failed"
    - - Skip submission record creation

  - 6. **Submission Record Management**:
    - a. Call _get_submission_status() to check for existing submission
    - b. Generate current timestamp using datetime.now().strftime()
    - c. Extract submission notes from submission_text.value (strip whitespace)
    - d. If notes empty, use default "Uploaded to link drive"
    - e. If existing submission found:
    - - Update existing['submitted_at'] with new timestamp
    - - Update existing['file_id'] from upload result
    - - Update existing['file_name'] from upload result
    - - Update existing['file_link'] from upload result
    - - Set existing['uploaded_to_drive'] to True
    - - Update existing['submission_text'] with notes
    - - Update existing['subject_folder'] with subject
    - f. If no existing submission:
    - - Create new submission dictionary with:
    - * id: timestamp-based unique identifier
    - * assignment_id: from assignment parameter
    - * student_email: from current_student_email
    - * submission_text: student notes
    - * submitted_at: current timestamp
    - * grade: None (not graded yet)
    - * feedback: None (no feedback yet)
    - * file_id, file_name, file_link: from upload result
    - * uploaded_to_drive: True
    - * subject_folder: assignment subject
    - - Append new submission to self.todo.submissions list

  - 7. **Persistence and UI Update**:
    - a. Call data_manager.save_submissions() with updated submissions list
    - b. Call display_assignments() to refresh main UI with new status
    - c. Sleep for 1 second to allow user to see success message
    - d. Call close_overlay(None) to automatically close dialog
    - e. Update page to reflect all changes

  - 8. **Error Handling**:
    - a. Catch any exceptions during upload or record creation
    - b. Update upload_status to "✗ Error: &#123;exception_message&#125;"
    - c. Show error snackbar with exception details
    - d. Update page to display error message

  - 9. **File Picker Registration**:
    - a. Create ft.FilePicker instance with on_result=on_file_picked
    - b. Append file_picker to page.overlay list
    - c. Update page to register picker in overlay system

  - 10. **Dialog Content Assembly**:
    - a. Create Column container with spacing=10 and scroll="auto"
    - b. Add assignment title text (bold, word-wrapped)
    - c. Add subject text (size 13, blue color)
    - d. Add divider for visual separation
    - e. Add submission_text field for student notes
    - f. Add 10px spacing container
    - g. Add responsive row with folder_display and change_folder_btn
    - h. Add help text "You can browse and select a subfolder if needed"
    - i. Add 5px spacing container
    - j. Add "Choose File" button with upload icon
    - k. Add upload_status text for progress feedback
    - l. Add 10px spacing container
    - m. Add "Close" button row aligned to right

  - 11. **Dialog Display**:
    - a. Call todo.show_overlay() with:
    - - content: assembled Column
    - - title: "Submit: &#123;assignment_title&#125;"
    - - width: 450px
    - b. Store returned overlay and close_overlay function
    - c. Dialog now visible to user, awaiting interaction

## Interactions

- **DriveService**: Validates availability and retrieves folder info
- **StorageManager**: Handles file upload to Drive via
- upload_submission_to_link_drive()
- **DataManager**: Persists submission records via save_submissions()
- **TodoView**: Accesses page, services, shows snackbars, overlays
- **FilePicker**: System file selection dialog
- **FilePreviewService**: Optional file preview (not in this method)

## Example

```python
# Student submits assignment
assignment = {
    'id': 'assign_123',
    'title': 'Python Project',
    'subject': 'Computer Science',
    'drive_folder_id': 'folder_abc123',
    'deadline': '2025-12-31T23:59:00'
    }
submission_mgr.submit_assignment_dialog(assignment)
# User interacts with dialog:
# 1. Optionally browses to select subfolder
# 2. Clicks "Choose File" and selects file
# 3. File uploads to Drive
# 4. Submission record created/updated
# 5. Dialog auto-closes on success
```

## See Also

- `view_submissions_dialog()`: Teacher grading interface
- `_get_submission_status()`: Retrieve existing submission
- `StorageManager`: File uploads
- `DriveService`: Drive operations
- `DataManager`: Data persistence

## Notes

- Requires Google Drive service to be configured and authenticated
- Assignment must have valid drive_folder_id linked
- Student email is extracted from current_student_email attribute
- File upload uses student name prefix for organization
- Submission timestamp captured at upload completion
- Dialog auto-closes 1 second after successful upload
- Previous submissions are updated rather than duplicated
- Upload errors display in-dialog status and snackbar notification
