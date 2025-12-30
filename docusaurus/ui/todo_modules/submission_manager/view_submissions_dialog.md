---
id: "view_submissions_dialog"
sidebar_position: 6
title: "view_submissions_dialog"
---

# ⚙️ view_submissions_dialog

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`submission_manager.py`](./submission_manager.py) | **Line:** 756
:::

Display teacher grading interface for viewing and grading submissions.

Creates a comprehensive modal dialog showing all students enrolled for an
assignment (filtered by target type), their submission status, timing
information, and grading controls. Supports inline grading, feedback entry,
file preview, and edit mode for existing grades.

## Parameters

- **`assignment`** (dict): Assignment dictionary containing: - id (str): Unique assignment identifier - title (str): Assignment title displayed in dialog header - target_for (str): Student filter - 'all', 'bridging', or 'regular' - deadline (str): ISO 8601 deadline for timing calculations
- **`force_edit_email`** (str, optional): If provided, automatically opens the grade editor for this specific student email, even if already graded. Defaults to None (show read-only view for graded submissions).

## Returns

**Type**: `None`

                Updates UI and data stores as side effects.

## Exceptions

No direct exceptions raised. All errors handled gracefully with:
            - Try-catch blocks around grade save operations
            - Snackbar notifications for save success/failure
            - Status text updates within dialog

## Algorithm

- 1. **Dialog Container Initialization**:
    - a. Create submissions_list Column with scroll="auto" and spacing=10
    - b. Initialize submitted_count counter to 0
    - c. Extract deadline from assignment dictionary
    - d. Create overlay and close_overlay using todo.show_overlay()
    - e. Set dialog title to "Submissions for: &#123;title&#125; (0/&#123;total&#125;)" initially
    - f. Set dialog dimensions: width=600px, height=500px

  - 2. **Student Filtering**:
    - a. Extract target_for value from assignment ('all', 'bridging', 'regular')
    - b. If target == 'bridging':
    - - Call student_manager.get_bridging_students()
    - - Store filtered list in target_students
    - c. If target == 'regular':
    - - Call student_manager.get_regular_students()
    - - Store filtered list in target_students
    - d. If target == 'all' or any other value:
    - - Use complete self.todo.students list as target_students
    - e. If target_students is empty:
    - - Append "No students enrolled" message to submissions_list
    - - Skip to step 10 (early completion)

  - 3. **Student Loop - Submission Status Retrieval**:
    - a. Begin for loop iterating through each student in target_students
    - b. Extract student_name from student['name']
    - c. Search self.todo.submissions for matching record:
    - - Match on: assignment_id == assignment['id']
    - - AND: student_email == student['email']
    - d. Store result in 'sub' variable (None if not found)

  - 4. **Submitted Assignment Processing**:
    - a. If sub is not None (submission exists):
    - i. Increment submitted_count by 1
    - ii. Create status_icon as green checkmark (ft.Icons.CHECK_CIRCLE)
    - iii. Set status_text to "Submitted: &#123;submitted_at&#125;"

  - 5. **Timing Calculation for Submissions**:
    - a. Call calculate_submission_timing() with:
    - - submitted_at: sub['submitted_at']
    - - deadline: assignment deadline
    - b. Receive timing_status ('early' or 'late' or None)
    - c. Receive timing_text (formatted message like "✅ 1d 13h early")
    - d. Set timing_color to GREEN if early, ORANGE if late
    - e. Create timing badge container with background color and text

  - 6. **Grading Mode Determination**:
    - a. Check if submission is already graded:
    - - is_graded = True if (grade exists OR feedback exists) AND not force_edit
    - b. If is_graded == True (Read-Only Mode):
    - i. Create grade_display Container with:
    - - Blue-tinted background (opacity 0.05)
    - - Border: 1px solid BLUE_200
    - - Padding: 10px, border_radius: 8px
    - ii. Display grade as "Grade: &#123;value&#125;" (bold, blue text)
    - iii. Display feedback as "Feedback: &#123;text&#125;" (bold label + text)
    - iv. Create "Edit Grade" button with edit icon
    - v. Define make_toggle_edit_handler() closure:
    - - Captures student_email and close_fn
    - - When clicked: closes dialog, reopens with force_edit_email
    - vi. Connect handler to "Edit Grade" button
    - vii. Display "Last updated: &#123;graded_at&#125;" if timestamp exists
    - viii. Assemble grade_section with display and edit button
    - c. If is_graded == False (Edit Mode):
    - i. Create grade_field TextField:
    - - Pre-filled with existing grade if available
    - - Label: "Grade", hint: "e.g., 95/100"
    - - Width: 150px
    - ii. Create feedback_field TextField:
    - - Pre-filled with existing feedback if available
    - - Label: "Feedback", multiline: True
    - - Min lines: 3, max lines: 5
    - iii. Create save_status Text (initially empty)
    - iv. Define make_save_handler() closure:
    - - Captures sub, student_name, close_fn
    - - Returns save_grade(e) function
    - v. Save handler implementation:
    - - Disable save button, set text to "Saving..."
    - - Update page to show disabled state
    - - Update sub['grade'] from grade_field.value
    - - Update sub['feedback'] from feedback_field.value
    - - Set sub['graded_at'] to current timestamp
    - - Call data_manager.save_submissions()
    - - Show success snackbar
    - - Close dialog and reopen (refreshes to read-only)
    - - On error: update save_status, re-enable button
    - vi. Create "Save Grade" button with save icon
    - vii. Connect save_handler to button click
    - viii. Assemble grade_section with fields and save button

  - 7. **File Access Controls**:
    - a. Initialize file_link_btn as empty Container
    - b. If sub.get('file_link') exists (has direct Drive link):
    - i. Create Row with two buttons:
    - - "Preview File" button (if file_preview service available)
    - - Click calls _preview_file() with file_id and file_name
    - - "Open in Browser" button
    - - Click calls _open_link() with file_link URL
    - ii. Set spacing to 10px between buttons
    - iii. Store in file_link_btn
    - c. Elif sub.get('file_id') exists (has Drive ID but no link):
    - i. Create Row with two buttons:
    - - "Preview File" button (if file_preview available)
    - - Click calls _preview_file() with file_id and file_name
    - - "Open in Browser" button
    - - Click calls _open_drive_file() with file_id
    - ii. Set spacing to 10px between buttons
    - iii. Store in file_link_btn

  - 8. **Submission Card Assembly**:
    - a. Create Column with card_content containing:
    - i. Row with status_icon and student name/email (bold, word-wrap)
    - ii. Status text (size 12, green, "Submitted: &#123;time&#125;")
    - iii. Timing badge container (if timing_status exists)
    - iv. Submission notes text (size 12, word-wrap)
    - v. File name text (size 12, blue color, word-wrap)
    - vi. File link buttons row
    - vii. Divider
    - viii. Grade section (read-only or edit mode)
    - b. Set card_border_color to GREEN_200
    - c. Set card_bg to GREEN_50
    - d. Wrap card_content in Container with:
    - - padding: 10px
    - - border: 1px solid card_border_color
    - - border_radius: 8px
    - - bgcolor: card_bg
    - e. Store wrapped container in 'card' variable

  - 9. **Missing Submission Processing**:
    - a. If sub is None (no submission found):
    - i. Create status_icon as red cancel icon (ft.Icons.CANCEL)
    - ii. Set status_text to "Missing"
    - iii. Create card_content as Row containing:
    - - status_icon (red cancel)
    - - Student name/email Container (bold, word-wrap, expand=True)
    - - status_text ("Missing" in red, bold)
    - iv. Set card_border_color to RED_200
    - v. Set card_bg to RED_50
    - vi. Wrap in Container with red theme styling
    - vii. Store wrapped container in 'card' variable

  - 10. **Card Addition and Counter Update**:
    - a. Append 'card' to submissions_list.controls
    - b. After all students processed, insert at position 0:
    - - Text showing "Submissions: &#123;submitted_count&#125;/&#123;total&#125;"
    - - Size: 16, bold, color: BLUE_700
    - c. Update dialog title to reflect accurate count
    - d. Call self.todo.page.update() to render all changes

  - 11. **Event Handler Persistence**:
    - a. All event handlers (save, edit, preview, open) remain active
    - b. Handlers use closures to capture submission references
    - c. Handlers persist until dialog is closed
    - d. Dialog can be reopened multiple times with different parameters

  - 12. **Force Edit Mode Handling**:
    - a. If force_edit_email parameter provided on dialog open:
    - i. When processing matching student, bypass is_graded check
    - ii. Force edit mode to display for that specific student
    - iii. All other students display normal read-only if graded
    - b. After "Edit Grade" button clicked:
    - i. Close current dialog instance
    - ii. Reopen view_submissions_dialog() with force_edit_email set
    - iii. This creates fresh dialog with edit mode active

## Interactions

- **StudentManager**: Retrieves filtered student lists via
- get_bridging_students(), get_regular_students()
- **DataManager**: Persists grade updates via save_submissions()
- **FilePreviewService**: Displays file previews via _preview_file()
- **DriveService**: Retrieves file info for drive links
- **TodoView**: Accesses submissions, students, shows snackbars/overlays
- **calculate_submission_timing()**: Computes early/late timing

## Example

```python
# Teacher views all submissions
assignment = {
    'id': 'assign_123',
    'title': 'Python Project',
    'target_for': 'all',
    'deadline': '2025-12-31T23:59:00'
    }
submission_mgr.view_submissions_dialog(assignment)
# Dialog shows:
# - 15/20 students submitted
# - 5 green cards (submitted, graded)
# - 10 green cards (submitted, needs grading)
# - 5 red cards (missing submission)

# Teacher edits existing grade
submission_mgr.view_submissions_dialog(
    assignment,
    force_edit_email='student@example.com'
    )
# Dialog opens with edit mode active for that student
```

## See Also

- `submit_assignment_dialog()`: Student submission interface
- `calculate_submission_timing()`: Timing calculation
- `_get_submission_status()`: Retrieve submission record
- `_preview_file()`: Launch file preview
- `StudentManager`: Student filtering
- `DataManager`: Grade persistence

## Notes

- Dialog is 600px wide, 500px tall with scrollable content
- Students filtered by assignment target_for (all/bridging/regular)
- Submission timing shows days, hours, minutes with emoji indicators
- Grade editing updates 'graded_at' timestamp automatically
- Edit mode accessible via "Edit Grade" button or force_edit_email
- Missing submissions clearly marked with red styling
- File preview requires FilePreviewService availability
- Browser links open in new tab via webbrowser module
- Save button disabled during save operation to prevent double-submit
- Dialog auto-refreshes after grade save to show read-only view
