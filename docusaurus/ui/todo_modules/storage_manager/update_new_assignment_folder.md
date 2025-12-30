---
id: "update_new_assignment_folder"
sidebar_position: 14
title: "update_new_assignment_folder"
---

# ⚙️ update_new_assignment_folder

![Completeness](https://img.shields.io/badge/Docs-20%25-red)

:::info Source
**File:** [`storage_manager.py`](./storage_manager.py) | **Line:** 624
:::

Update the UI with the selected folder's name.

## Purpose

Callback used by the folder picker to update the assignment form state.

## Parameters

- **`fid`** (str): Selected Drive folder ID.

## Interactions

- Calls `drive_service.get_file_info` (to show name).
- Updates `todo.drive_folder_label`.
- Updates `todo.selected_drive_folder_id`.
