---
id: "display_teacher_view"
sidebar_position: 8
title: "display_teacher_view"
---

# ⚙️ display_teacher_view

![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-0%25-red)

:::info Source
**File:** [`assignment_manager.py`](./assignment_manager.py) | **Line:** 373
:::

Render the assignment list for the teacher mode.

## Purpose

Displays assignments with administrative controls (Edit, Delete, View Submissions).

## Algorithm

- 1. Get current filter (All, Active, Completed, Overdue).
  - 2. Filter `todo.assignments` based on deadline status.
  - 3. If empty -> Show placeholder.
  - 4. Else -> Loop through assignments, create cards, append to UI column.

## Interactions

- Reads `todo.assignments`.
- Reads `todo.filter_dropdown`.
- Calls `create_teacher_assignment_card`.
