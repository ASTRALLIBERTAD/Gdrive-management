---
id: "create_teacher_assignment_card"
sidebar_position: 10
title: "create_teacher_assignment_card"
---

# ⚙️ create_teacher_assignment_card

![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`assignment_manager.py`](./assignment_manager.py) | **Line:** 483
:::

Build a UI card for an assignment (Teacher View).

## Purpose

Generates a visual card component containing assignment details and management actions.

## Parameters

- **`assignment`** (dict): Assignment data object.

## Returns

**Type**: `ft.Container`


## Algorithm

- 1. Calculate statistics (status, time remaining, submission count).
  - 2. Build status badge.
  - 3. Build Drive folder link (if linked).
  - 4. Build Attachment preview/link (if present).
  - 5. Build Management Buttons (View Submissions, Edit, Delete).
  - 6. Assemble into styled Container.

## Interactions

- Calls `view_submissions_dialog` (via button).
- Calls `edit_assignment_dialog` (via button).
- Calls `delete_assignment` (via button).
