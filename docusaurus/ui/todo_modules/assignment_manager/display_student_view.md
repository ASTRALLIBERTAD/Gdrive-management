---
id: "display_student_view"
sidebar_position: 9
title: "display_student_view"
---

# ⚙️ display_student_view

![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-0%25-red)

:::info Source
**File:** [`assignment_manager.py`](./assignment_manager.py) | **Line:** 408
:::

Render the assignment list for the student mode.

## Purpose

Displays relevant assignments for the logged-in student, respecting bridging/regular status.

## Algorithm

- 1. Check notifications -> show alert if unread messages exist.
  - 2. Verify student selected; if not, show error.
  - 3. Determine student type (Bridging vs Regular).
  - 4. Filter assignments:
    - a. Match target audience (All vs Matching Type).
    - b. Apply status filter (Active, etc.).
  - 5. Render cards or empty state.

## Interactions

- Reads `todo.assignments`, `todo.students`.
- Calls `notification_service` for unread counts.
- Calls `create_student_assignment_card`.
