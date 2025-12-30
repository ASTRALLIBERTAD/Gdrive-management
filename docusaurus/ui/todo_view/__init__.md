---
id: "__init__"
sidebar_position: 3
title: "__init__"
---

# 🔧 __init__

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`todo_view.py`](./todo_view.py) | **Line:** 268
:::

Initialize TodoView with page, navigation callback, and Drive service.

Constructs the LMS view by setting up data persistence, instantiating
manager subsystems, loading existing data, and initializing all UI
components. Prepares the complete application state for rendering.

## Parameters

- **`page`** (ft.Page): Flet page instance for UI rendering, updates, and overlay management. Must be initialized and active.
- **`on_back`** (Callable, optional): Callback function invoked when user clicks back button. Typically navigates to dashboard. Signature: () -> None. Defaults to None (back button hidden).
- **`drive_service`** (DriveService, optional): Google Drive service wrapper providing file/folder operations. If None, Drive features are disabled or degraded. Defaults to None.

## Algorithm

- 1. **Store Core References**:
    - a. Assign page to self.page
    - b. Assign on_back to self.on_back
    - c. Assign drive_service to self.drive_service

  - 2. **Setup Data Directory**:
    - a. Create Path object: Path("lms_data")
    - b. Store in self.data_dir
    - c. Call mkdir(exist_ok=True) to create if needed
    - d. Directory contains JSON files for persistence

  - 3. **Import Manager Classes**:
    - a. Import DataManager from ui.todo_modules.data_manager
    - b. Import StorageManager from ui.todo_modules.storage_manager
    - c. Import AssignmentManager from ui.todo_modules.assignment_manager
    - d. Import StudentManager from ui.todo_modules.student_manager
    - e. Import SubmissionManager from ui.todo_modules.submission_manager

  - 4. **Instantiate Managers**:
    - a. Create DataManager(data_dir, drive_service)
    - b. Create StorageManager(self, drive_service)
    - c. Create AssignmentManager(self)
    - d. Create StudentManager(self)
    - e. Create SubmissionManager(self)
    - f. Each manager stores reference to TodoView (self)

  - 5. **Load Persistent Data**:
    - a. Call data_manager.load_assignments() -> list
    - b. Store in self.assignments
    - c. Call data_manager.load_students() -> list
    - d. Store in self.students
    - e. Call data_manager.load_submissions() -> list
    - f. Store in self.submissions
    - g. Call self.load_saved_links() -> list
    - h. Store in self.saved_links

  - 6. **Initialize Notification Service** (optional):
    - a. Try to import NotificationService
    - b. If successful:
    - i. Instantiate NotificationService(data_dir)
    - ii. Store in self.notification_service
    - c. If ImportError:
    - i. Set self.notification_service = None
    - ii. Feature gracefully disabled

  - 7. **Set Initial State**:
    - a. Set self.current_mode = "teacher"
    - b. Set self.current_student_email = None
    - c. Default view is teacher mode with no student selected

  - 8. **Initialize UI Components**:
    - a. Call self._init_ui_components()
    - b. Creates all input fields, dropdowns, pickers, etc.
    - c. Stores components as instance attributes
    - d. Components ready for get_view() to assemble

## Interactions

- **Path.mkdir()**: Creates data directory
- **DataManager**: Loads assignments, students, submissions
- **load_saved_links()**: Loads legacy link shortcuts
- **_init_ui_components()**: Creates UI controls
- **Manager classes**: Instantiated with references

## Example

```python
# Create with full configuration
todo = TodoView(
    page=page,
    on_back=lambda: page.go('/dashboard'),
    drive_service=drive
    )
print(len(todo.assignments))
# 5
print(todo.current_mode)
# teacher

# Create with minimal configuration
todo_minimal = TodoView(page=page)
print(todo_minimal.on_back)
# None
print(todo_minimal.drive_service)
# None
```

## See Also

- `_init_ui_components()`: Initializes UI controls
- `load_saved_links()`: Loads legacy link data
- `get_view()`: Assembles UI layout
- `DataManager`: Data persistence

## Notes

- Data directory created automatically if doesn't exist
- Manager instantiation order important (DataManager first)
- In-memory data lists updated by managers throughout lifecycle
- Notification service optional (None if import fails)
- Drive service optional (features degrade gracefully if None)
- Initial mode is teacher (assignments writable)
- UI components not attached to page until get_view() called
