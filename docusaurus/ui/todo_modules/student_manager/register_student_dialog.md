---
id: "register_student_dialog"
sidebar_position: 6
title: "register_student_dialog"
---

# ⚙️ register_student_dialog

![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-20%25-red)

:::info Source
**File:** [`student_manager.py`](./student_manager.py) | **Line:** 188
:::

Show student registration dialog.

## Purpose

Handles the self-registration flow for new students, ensuring unique emails
            and capturing necessary metadata (Student ID, Bridging Status).

## Parameters

- **`e`** (ft.ControlEvent, optional): Trigger event.

## Algorithm

- 1. Display form (Name, Email, ID, Bridging Switch).
  - 2. On Register:
    - a. Validate inputs (required fields, gmail format, uniqueness).
    - b. Create student dictionary.
    - c. Append to list and Save.
    - d. Auto-login (set current student).
    - e. Refresh main view.

## Interactions

- Validates against `todo.students` (uniqueness).
- Calls `todo.data_manager.save_students`.
- Updates `todo.current_student_email`.
- Calls `todo.display_assignments` (refresh view).
