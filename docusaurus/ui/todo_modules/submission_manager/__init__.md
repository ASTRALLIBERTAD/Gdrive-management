---
id: "__init__"
sidebar_position: 3
title: "__init__"
---

# 🔧 __init__

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`submission_manager.py`](./submission_manager.py) | **Line:** 177
:::

Initialize the SubmissionManager with parent view reference.

Sets up the submission manager by storing a reference to the parent TodoView
and attempting to initialize the FilePreviewService. If the service cannot
be imported or initialized, file preview functionality will be disabled but
other features remain functional.

## Parameters

- **`todo_view`** (TodoView): Parent TodoView instance that provides access to: - page: Flet page object for UI updates - drive_service: Google Drive integration service - data_manager: Persistent data storage manager - storage_manager: File upload and Drive operations - student_manager: Student data and filtering - submissions: List of all submission records - students: List of all student records - current_student_email: Currently logged-in student

## Algorithm

- 1. Receive and store reference to parent TodoView instance
  - 2. Initialize temp_file_path attribute to None (used during upload operations)
  - 3. Initialize temp_file_name attribute to None (used during upload operations)
  - 4. Enter try-except block for FilePreviewService initialization
  - 5. Attempt to import FilePreviewService from services.file_preview_service module
  - 6. If import successful:
    - a. Instantiate FilePreviewService with todo_view.page parameter
    - b. Pass todo_view.drive_service as second parameter
    - c. Store instance in self.file_preview attribute
  - 7. If ImportError occurs (service not available):
    - a. Catch the exception silently
    - b. Set self.file_preview to None
    - c. File preview functionality will be disabled but other features work
  - 8. Initialization complete, instance ready for use

## Interactions

- **TodoView**: Stores reference for accessing shared services
- **FilePreviewService**: Conditionally imported and initialized

## Example

```python
from src.ui.views.todo_view import TodoView
todo_view = TodoView(page, user_data)
submission_mgr = SubmissionManager(todo_view)
print(f"Preview available: {submission_mgr.file_preview is not None}")
# Preview available: True
```

## See Also

- `TodoView`: Parent view class
- `FilePreviewService`: File preview service

## Notes

- File preview is optional; other features work without it
- Temporary file attributes are reset after each submission
