---
id: "delete_assignment"
sidebar_position: 18
title: "delete_assignment"
---

# ⚙️ delete_assignment

![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-20%25-red)

:::info Source
**File:** [`assignment_manager.py`](./assignment_manager.py) | **Line:** 1060
:::

Show confirmation dialog to delete an assignment.

## Purpose

Permanently removes an assignment and all its associated submissions.

## Parameters

- **`assignment`** (dict): Assignment to delete.

## Algorithm

- 1. Show confirmation dialog.
  - 2. On Confirm:
    - a. Filter out assignment from list.
    - b. Filter out linked submissions from list.
    - c. Save updated lists.
    - d. Refresh display and show snackbar.

## Interactions

- Modifies `todo.assignments`, `todo.submissions`.
- Calls `data_manager.save_assignments`, `save_submissions`.
