---
id: "submissionmanager"
sidebar_position: 2
title: "SubmissionManager"
---

# 📦 SubmissionManager

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Completeness](https://img.shields.io/badge/Docs-20%25-red)

:::info Source
**File:** [`submission_manager.py`](./submission_manager.py) | **Line:** 17
:::

Manages the submission and grading process for student assignments.

The SubmissionManager class orchestrates the complete lifecycle of assignment
submissions in an educational application. It provides a dual-interface system:
a student-facing submission portal for uploading work with notes, and a
teacher-facing grading interface for evaluating submissions and providing feedback.
This class integrates with Google Drive for file storage, calculates submission
timing metrics (early/late relative to deadlines), and manages the persistent
storage of submission records and grades through the DataManager.

## Purpose

- Enable students to submit assignment files with optional notes
        - Provide teachers with a comprehensive grading interface
        - Calculate and display submission timing (early/late) relative to deadlines
        - Manage file uploads to Google Drive with organized folder structures
        - Persist submission data and grades across application sessions
        - Support file preview functionality for submitted work

## Attributes

- **`todo`** (TodoView): Reference to the parent TodoView instance, providing access to shared services, data stores, and UI components.
- **`temp_file_path`** (str or None): Temporary storage for file path during upload operations. Reset after each submission.
- **`temp_file_name`** (str or None): Temporary storage for file name during upload operations. Reset after each submission.
- **`file_preview`** (FilePreviewService or None): Service instance for rendering file previews in overlays. None if import fails or service unavailable.

## Interactions

- **TodoView**: Parent class providing access to page, data_manager,
- drive_service, storage_manager, student_manager, and UI utilities
- **DataManager**: Persists submission records via save_submissions()
- **DriveService**: Handles Google Drive file operations and folder queries
- **StorageManager**: Uploads files to Drive with organized naming conventions
- **StudentManager**: Retrieves filtered student lists (bridging/regular/all)
- **FilePreviewService**: Renders file previews in modal overlays
- Algorithm (High-Level Workflow):
- *Phase 1: Initialization**
- 1. Receive TodoView instance reference containing all shared services
- 2. Initialize temporary file storage attributes (temp_file_path, temp_file_name)
- 3. Attempt to import FilePreviewService from services module
- 4. If import successful, instantiate service with page and drive_service
- 5. If import fails, set file_preview to None (graceful degradation)
- *Phase 2: Student Submission Process** (submit_assignment_dialog)
- 1. Validate that Google Drive service is connected and available
- 2. Verify that assignment has a linked Drive folder ID
- 3. Display submission dialog with assignment details and subject
- 4. Initialize folder display showing the target upload location
- 5. Provide optional folder browser for subfolder selection
- 6. Present file picker for student to select assignment file
- 7. When file selected, extract file path, name, and student identifier
- 8. Upload file to Drive using StorageManager with student name prefix
- 9. Retrieve existing submission record or create new submission object
- 10. Populate submission with file metadata (id, name, link) and timestamp
- 11. Update or append submission to submissions list
- 12. Persist changes through DataManager.save_submissions()
- 13. Refresh UI to display updated submission status
- 14. Show success notification and auto-close dialog after 1 second
- *Phase 3: Teacher Grading Process** (view_submissions_dialog)
- 1. Create scrollable dialog container for submission cards
- 2. Retrieve assignment's target_for filter (all/bridging/regular students)
- 3. Call StudentManager to get filtered list of target students
- 4. Initialize submission counter for tracking submitted vs total
- 5. For each student in target list:
- a. Search submissions list for matching assignment_id and student_email
- b. If submission exists:
- Increment submitted counter
- Calculate submission timing using calculate_submission_timing()
- Determine if already graded (has grade or feedback)
- If graded and not force_edit: display read-only grade view
- If not graded or force_edit matches: display editable grade fields
- Add file preview and browser links if file available
- Create green-themed card with all submission details
- c. If submission missing:
- Create red-themed card with "Missing" status
- d. Append card to submissions list container
- 6. Insert submission count summary at top of dialog
- 7. When "Save Grade" clicked:
- a. Disable save button to prevent double-submission
- b. Update submission record with grade and feedback
- c. Add graded_at timestamp
- d. Persist via DataManager.save_submissions()
- e. Close dialog and reopen to show read-only view
- 8. When "Edit Grade" clicked:
- a. Close current dialog
- b. Reopen with force_edit_email parameter set
- c. This switches from read-only to edit mode
- *Phase 4: Timing Calculation** (calculate_submission_timing)
- 1. Validate that both submitted_at and deadline strings are provided
- 2. Return (None, "No timing data") if either parameter is missing
- 3. Parse submitted_at timestamp:
- If contains 'T', parse as ISO 8601 format
- Otherwise, parse as '%Y-%m-%d %H:%M' format
- 4. Parse deadline timestamp as ISO 8601 format
- 5. Calculate time difference: time_diff = deadline - submitted_at
- 6. Check if time_diff is positive (early) or negative (late)
- 7. If early (positive difference):
- a. Extract days, hours, minutes from time_diff
- b. Format message prioritizing largest non-zero unit
- c. Return ("early", "✅ &#123;days&#125;d &#123;hours&#125;h early") or similar
- 8. If late (negative difference):
- a. Take absolute value of time_diff
- b. Extract days, hours, minutes from absolute time_diff
- c. Format message prioritizing largest non-zero unit
- d. Return ("late", "⚠️ &#123;days&#125;d &#123;hours&#125;h late") or similar
- 9. If any parsing or calculation error occurs:
- Catch exception and return (None, "Invalid timing data")

## Example

```python
# Initialize with TodoView instance
submission_mgr = SubmissionManager(todo_view)

# Student submits an assignment
assignment = {
    'id': 'assign_123',
    'title': 'Python Project',
    'subject': 'Computer Science',
    'drive_folder_id': 'folder_xyz',
    'deadline': '2025-12-31T23:59:00'
    }
submission_mgr.submit_assignment_dialog(assignment)

# Teacher views submissions and grades
submission_mgr.view_submissions_dialog(assignment)

# Calculate timing for a submission
status, msg = submission_mgr.calculate_submission_timing(
    '2025-12-30T10:00:00',
    '2025-12-31T23:59:00'
    )
print(f"Status: {status}, Message: {msg}")
# Status: early, Message: ✅ 1d 13h early
```

## See Also

- `TodoView`: Parent view class
- `FilePreviewService`: File preview service
- `DataManager`: Data persistence layer
- `DriveService`: Google Drive integration
- `StorageManager`: File upload manager
- `StudentManager`: Student data manager

## Notes

- All file uploads include student identifier for organization
- Submission timing uses ISO 8601 datetime format
- Grade editing requires force_edit_email parameter to reopen editor
- File preview requires FilePreviewService to be available
- Missing submissions are clearly marked in teacher interface

## References

- Google Drive API: [https://developers.google.com/drive](https://developers.google.com/drive)
- Flet UI Framework: [https://flet.dev](https://flet.dev)
- ISO 8601 Datetime Standard: [https://en.wikipedia.org/wiki/ISO_8601](https://en.wikipedia.org/wiki/ISO_8601)
