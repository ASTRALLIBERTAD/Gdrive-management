---
id: "storagemanager"
sidebar_position: 2
title: "StorageManager"
---

# 📦 StorageManager

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-20%25-red)

:::info Source
**File:** [`storage_manager.py`](./storage_manager.py) | **Line:** 20
:::

Manages Google Drive storage operations for the LMS.

## Attributes

- **`todo`** (TodoView): Reference to the main application view for accessing shared state (like DataManager).
- **`drive_service`** (DriveService): The service wrapper for making Google Drive API calls.
- **`subject_folders_cache`** (dict): In-memory cache mapping subject names to Drive Folder IDs.

## Examples

```python
storage = StorageManager(todo_view, drive_service)
folder_id = storage.get_or_create_subject_folder_in_lms("Physics")
storage.upload_assignment_attachment("test.pdf", "test.pdf", "Physics", "123")
```

## See Also

- `DriveService`
- `DataManager`
