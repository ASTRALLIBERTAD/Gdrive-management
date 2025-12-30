---
id: "create_student_assignment_card"
sidebar_position: 11
title: "create_student_assignment_card"
---

# ⚙️ create_student_assignment_card

![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`assignment_manager.py`](./assignment_manager.py) | **Line:** 633
:::

Build a UI card for an assignment (Student View).

## Purpose

Generates a visual card for students to view details and submit work.

## Parameters

- **`assignment`** (dict): Assignment data object.

## Returns

**Type**: `ft.Container`


## Algorithm

- 1. Determine status (Active/Overdue) and submission state (Submitted/Not).
  - 2. Build Attachment section (Download/Preview).
  - 3. Build Submission Status section (Grade, Feedback).
  - 4. Build Action Buttons:
    - a. "Submit Assignment" (if active/not submitted).
    - b. "Resubmit" (if submitted).
    - c. "Preview Submission" (if file uploaded).
  - 5. Assemble into styled Container.

## Interactions

- Checks `submissions` for current student status.
- Calls `submission_manager.submit_assignment_dialog`.
