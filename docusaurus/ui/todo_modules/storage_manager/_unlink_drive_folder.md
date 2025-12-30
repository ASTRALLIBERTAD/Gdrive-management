---
id: "_unlink_drive_folder"
sidebar_position: 9
title: "_unlink_drive_folder"
---

# ⚙️ _unlink_drive_folder

![Completeness](https://img.shields.io/badge/Docs-0%25-red)

:::info Source
**File:** [`storage_manager.py`](./storage_manager.py) | **Line:** 305
:::

Remove the link to the Google Drive root folder.

## Purpose

Resets the application to use local storage only by removing the LMS Root ID from config.

## Interactions

- Reads/Writes `lms_config.json`.
- Updates `todo.data_manager.lms_root_id`.
- Refreshes UI (Assignments, Students).
