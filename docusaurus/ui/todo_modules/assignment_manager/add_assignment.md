---
id: "add_assignment"
sidebar_position: 4
title: "add_assignment"
---

# ⚙️ add_assignment

![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-20%25-red)

:::info Source
**File:** [`assignment_manager.py`](./assignment_manager.py) | **Line:** 71
:::

Handle the creation of a new assignment.

## Purpose

Validates inputs, processes file uploads, creates assignment record, saves to DB, and notifies students.

## Parameters

- **`e`** (ft.ControlEvent): Trigger event (usually 'Create' button click).

## Algorithm

- 1. Extract values from UI fields.
  - 2. Validate: Title required, Subject required, Deadline must be future.
  - 3. If invalid -> `show_validation_errors`, exit.
  - 4. Create assignment dictionary (ID, timestamps, status).
  - 5. File Handling:
    - a. If attachment selected: Call `upload_assignment_attachment`.
    - b. Update assignment dict with upload result (Drive ID, link).
  - 6. Append to `todo.assignments`.
  - 7. Save to persistent storage.
  - 8. Send notifications to students.
  - 9. Reset form and refresh display.

## Interactions

- Reads inputs from `todo` fields (title, desc, subject, deadline, attachment).
- Calls `storage_manager.upload_assignment_attachment`.
- Calls `data_manager.save_assignments`.
- Calls `notification_service.notify_new_assignment`.
