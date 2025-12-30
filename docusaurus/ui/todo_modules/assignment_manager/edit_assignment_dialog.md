---
id: "edit_assignment_dialog"
sidebar_position: 17
title: "edit_assignment_dialog"
---

# ⚙️ edit_assignment_dialog

![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-20%25-red)

:::info Source
**File:** [`assignment_manager.py`](./assignment_manager.py) | **Line:** 920
:::

Open a dialog to edit an existing assignment.

## Purpose

Provides a form to modify assignment details (Title, Description, Score, Attachment, Folder, Audience).

## Parameters

- **`assignment`** (dict): Assignment data to edit.

## Algorithm

- 1. Pre-fill UI fields with current data.
  - 2. Setup FilePicker for replacing attachment.
  - 3. Setup Folder Browser for changing submission folder.
  - 4. On Save:
    - a. Update simple fields (title, desc, score).
    - b. If attachment changed -> Upload new file -> Update IDs/Link.
    - c. Save to DataManager.
    - d. Refresh UI.

## Interactions

- Calls `storage_manager.create_browse_dialog` (Folder picker).
- Calls `data_manager.save_assignments`.
- Calls `storage_manager.upload_assignment_attachment` (if new file picked).
