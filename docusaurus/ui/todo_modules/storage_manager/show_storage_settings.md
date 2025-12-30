---
id: "show_storage_settings"
sidebar_position: 8
title: "show_storage_settings"
---

# ⚙️ show_storage_settings

![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-0%25-red)

:::info Source
**File:** [`storage_manager.py`](./storage_manager.py) | **Line:** 253
:::

Show configuration dialog for LMS storage settings.

## Purpose

Provides a UI for the user to view the current LMS Root folder status
            and choose to Link (select from Drive) or Unlink (use local only).

## Algorithm

- 1. Check current `lms_root_id`.
  - 2. If set, fetch its name via Drive API.
  - 3. Build UI: Display current folder name.
  - 4. Buttons: "Select/Change Drive Folder", "Unlink".
  - 5. Helper functions bind actions to close overlay and proceed.

## Interactions

- Calls `todo.show_overlay`.
- Calls `select_drive_folder_dialog` (if requested).
- Calls `_unlink_drive_folder` (if requested).
