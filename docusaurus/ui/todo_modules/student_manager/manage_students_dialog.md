---
id: "manage_students_dialog"
sidebar_position: 5
title: "manage_students_dialog"
---

# ⚙️ manage_students_dialog

![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-20%25-red)

:::info Source
**File:** [`student_manager.py`](./student_manager.py) | **Line:** 97
:::

Show dialog to manage (view/delete) registered students.

## Purpose

Provides an administrative interface to list all students, manually add new ones,
            or remove existing ones from the system.

## Parameters

- **`e`** (ft.ControlEvent): Trigger event (InputEvent or ClickEvent).

## Algorithm

- 1. Define internal `refresh_list` function to rebuild UI list.
  - 2. Define `add_student` handler:
    - a. Validate inputs.
    - b. Append new student dict.
    - c. Save to DataManager.
  - 3. Define `remove_student` handler:
    - a. Remove from list.
    - b. Save.
  - 4. Build UI structure (Form + List).
  - 5. Display via Overlay.

## Interactions

- Modifies `todo.students`.
- Calls `todo.data_manager.save_students`.
- Calls `update_student_dropdown`.
- Calls `todo.show_overlay`.
