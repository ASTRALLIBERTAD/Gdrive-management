---
id: "todoview"
sidebar_position: 2
title: "TodoView"
---

# 📦 TodoView

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Completeness](https://img.shields.io/badge/Docs-20%25-red)

:::info Source
**File:** [`todo_view.py`](./todo_view.py) | **Line:** 26
:::

Main orchestrator and UI controller for the Learning Management System.

TodoView serves as the central hub that coordinates all LMS functionality,
integrating assignment management, student administration, file storage,
submission tracking, and UI presentation. It manages the view state (teacher
vs student mode), handles persistent data loading/saving, and provides the
primary interface for both educators and learners.
This class follows the Facade pattern, presenting a unified interface to
multiple complex subsystems (assignments, students, storage, submissions).
It maintains the application state, manages UI components, and delegates
specialized operations to manager classes while handling cross-cutting
concerns like overlays, snackbars, and navigation.

## Purpose

- Orchestrate interactions between UI and manager subsystems
        - Maintain application state (mode, current user, selections)
        - Provide unified interface for LMS functionality
        - Handle persistent data loading and saving
        - Manage UI layout and component lifecycle
        - Support role-based views (teacher/student modes)
        - Facilitate file attachments and Drive integration
        - Display assignments, students, and submissions

## Attributes

- **`page`** (ft.Page): Flet page instance for UI rendering and updates. Provides access to overlay system, update mechanism, and platform detection.
- **`on_back`** (Callable or None): Optional callback function invoked when user clicks back button to return to dashboard. Signature: () -> None.
- **`drive_service`** (DriveService or None): Google Drive service wrapper providing file/folder operations, metadata queries, and permissions management. May be None if Drive integration unavailable.
- **`data_dir`** (Path): Local directory path for storing LMS data files (assignments.json, students.json, submissions.json). Created automatically if doesn't exist.
- **`data_manager`** (DataManager): Manager handling JSON serialization, deserialization, and persistence of assignments, students, and submissions data.
- **`storage_manager`** (StorageManager): Manager coordinating Drive folder operations, link handling, and file upload/download functionality.
- **`assignment_manager`** (AssignmentManager): Manager implementing assignment CRUD operations, rendering logic, and deadline calculations.
- **`student_manager`** (StudentManager): Manager handling student registration, enrollment, type classification (bridging/regular), and dropdown population.
- **`submission_manager`** (SubmissionManager): Manager coordinating submission flow, grading interface, file preview, and timing calculations.
- **`assignments`** (list): In-memory list of assignment dictionaries. Each assignment contains: id, title, description, subject, deadline, drive_folder_id, file_path, file_name, max_score, target_for, etc.
- **`students`** (list): In-memory list of student dictionaries. Each student contains: email, name, student_type ('bridging' or 'regular').
- **`submissions`** (list): In-memory list of submission dictionaries. Each submission contains: id, assignment_id, student_email, submitted_at, grade, feedback, file_id, file_name, file_link, etc.
- **`saved_links`** (list): Legacy list of saved Drive folder shortcuts. Each link: &#123;id, name, url&#125;. Loaded from saved_links.json.
- **`notification_service`** (NotificationService or None): Optional service for managing assignment notifications and reminders. None if import fails.
- **`current_mode`** (str): Active view mode. Values: 'teacher' (default) or 'student'. Controls UI visibility and available operations.
- **`current_student_email`** (str or None): Email of currently selected student in student view mode. None if no student selected.
- **`assignment_title`** (ft.TextField): Input field for assignment title.
- **`assignment_description`** (ft.TextField): Multiline input for assignment instructions/description.
- **`subject_dropdown`** (ft.Dropdown): Subject selection dropdown with predefined options (Math, Science, English, etc.).
- **`max_score_field`** (ft.TextField): Numeric input for maximum assignment score.
- **`target_dropdown`** (ft.Dropdown): Target audience selector (All/Bridging/Regular).
- **`selected_drive_folder_id`** (str or None): Currently selected Drive folder ID for assignment attachment.
- **`drive_folder_label`** (ft.Text): Display text showing selected folder name.
- **`attachment_text`** (ft.Text): Display text showing attached file name.
- **`selected_attachment`** (dict): Dictionary with 'path' and 'name' keys for local file attachment.
- **`selected_date_value`** (datetime.date or None): Selected deadline date.
- **`selected_time_value`** (datetime.time or None): Selected deadline time.
- **`selected_deadline_display`** (ft.Text): Display text showing combined date and time deadline.
- **`date_picker`** (ft.DatePicker): Date picker dialog control.
- **`time_picker`** (ft.TimePicker): Time picker dialog control.
- **`assignment_column`** (ft.Column): Scrollable container displaying assignment cards. Updated dynamically based on mode and filters.
- **`filter_dropdown`** (ft.Dropdown): Filter selector for assignments (All/Active/Completed/Overdue).
- **`mode_switch`** (ft.Switch): Toggle control for teacher/student mode.
- **`mode_label`** (ft.Text): Display label showing current mode with emoji.
- **`settings_btn`** (ft.ElevatedButton): Button opening storage settings dialog.
- **`student_dropdown`** (ft.Dropdown): Student selector in student view mode.
- **`student_selector_row`** (ft.Row): Container for student selection controls, visible only in student mode.
- **`form_container`** (ft.Container or None): Container wrapping assignment creation form, visible only in teacher mode.
- **`manage_students_btn`** (ft.ElevatedButton or None): Button opening student management dialog, visible only in teacher mode.

## Interactions

- **DataManager**: Loads/saves assignments, students, submissions
- **StorageManager**: Handles Drive folder selection and file uploads
- **AssignmentManager**: Renders assignments and handles CRUD operations
- **StudentManager**: Manages student data and dropdown population
- **SubmissionManager**: Coordinates submission and grading workflows
- **DriveService**: Provides Drive API operations (if available)
- **NotificationService**: Manages notifications (if available)
- **ft.Page**: Updates UI and manages overlays/dialogs
- Algorithm (High-Level Workflow):
- *Phase 1: Initialization**
- 1. Store page, callback, and Drive service references
- 2. Create data directory (lms_data) if not exists
- 3. Import and instantiate manager classes:
- DataManager for persistence
- StorageManager for Drive operations
- AssignmentManager for assignment logic
- StudentManager for student management
- SubmissionManager for submission handling
- 4. Load persistent data:
- assignments from data_manager
- students from data_manager
- submissions from data_manager
- saved_links from JSON file
- 5. Optionally initialize NotificationService
- 6. Set default state: teacher mode, no student selected
- 7. Initialize all UI components via _init_ui_components()
- *Phase 2: UI Component Initialization** (_init_ui_components)
- 1. Create input fields (title, description, max_score)
- 2. Create dropdowns (subject, target, filter, student)
- 3. Create pickers (date, time, file)
- 4. Create display texts (folder, attachment, deadline)
- 5. Create layout containers (assignment_column, form_container)
- 6. Create controls (mode_switch, mode_label, buttons)
- 7. Store all components as instance attributes
- *Phase 3: View Rendering** (get_view)
- 1. Display current assignments via display_assignments()
- 2. Build assignment creation form (teacher mode only)
- 3. Create header with back button, icon, title
- 4. Build mode switcher row with settings button
- 5. Add student selector row (student mode only)
- 6. Add form container (teacher mode only)
- 7. Build assignment list section with filter
- 8. Assemble complete layout in Column
- 9. Return root Column control
- *Phase 4: Mode Switching** (switch_mode)
- 1. Toggle current_mode based on switch value
- 2. Update mode_label text and emoji
- 3. Show/hide student selector row
- 4. Show/hide form container
- 5. Show/hide manage students button
- 6. Refresh assignment display
- 7. Update page
- *Phase 5: Assignment Display** (display_assignments)
- 1. Clear assignment_column controls
- 2. Check current_mode
- 3. If teacher: delegate to assignment_manager.display_teacher_view()
- 4. If student: delegate to assignment_manager.display_student_view()
- 5. Update page to render changes
- *Phase 6: Data Interaction**
- 1. User creates/edits/deletes assignment
- 2. Manager updates in-memory list
- 3. DataManager saves to JSON file
- 4. UI refreshes to show changes
- *Phase 7: File/Folder Selection**
- 1. User clicks file/folder picker button
- 2. Picker dialog opens
- 3. User selects file/folder
- 4. Callback updates selected_* attributes
- 5. Display text updates to show selection
- 6. Page updates to render changes

## Example

```python
# Initialize TodoView with page and services
todo_view = TodoView(
    page=page,
    on_back=lambda: page.go('/dashboard'),
    drive_service=drive
    )

# Get view layout and add to page
layout = todo_view.get_view()
page.add(layout)
page.update()

# User in teacher mode sees:
# - Assignment creation form
# - List of all assignments
# - Manage students button

# User switches to student mode
todo_view.switch_mode(switch_event)
# User now sees:
# - Student selector dropdown
# - Assignments assigned to selected student
# - Submit buttons on assignments

# Display success message
todo_view.show_snackbar("Assignment created!", ft.Colors.GREEN)
```

## See Also

- `DataManager`: Data persistence
- `AssignmentManager`: Assignment logic
- `StudentManager`: Student management
- `SubmissionManager`: Submission handling
- `StorageManager`: Drive operations
- `Dashboard`: Parent dashboard container
- `DriveService`: Drive API wrapper

## Notes

- Data directory created automatically on initialization
- Manager classes receive self reference for accessing shared state
- In-memory data lists modified by managers, saved by DataManager
- UI components stored as attributes for dynamic updates
- Mode switch controls visibility of role-specific components
- Drive service optional - features gracefully degrade if None
- Notification service optional - loaded conditionally
- Overlay system supports modal dialogs with custom content
- Snackbar provides transient notifications
- Filter dropdown dynamically updates assignment display
- Student dropdown includes registration option
- File attachments support local files and Drive folders
- Deadline selection uses two-step process (date then time)

## References

- Flet Framework: [https://flet.dev/docs/](https://flet.dev/docs/)
- Facade Pattern: [https://refactoring.guru/design-patterns/facade](https://refactoring.guru/design-patterns/facade)
- Google Drive API: [https://developers.google.com/drive/api/v3/reference](https://developers.google.com/drive/api/v3/reference)
