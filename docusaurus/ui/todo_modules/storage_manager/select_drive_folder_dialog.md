---
id: "select_drive_folder_dialog"
sidebar_position: 10
title: "select_drive_folder_dialog"
---

# ⚙️ select_drive_folder_dialog

![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-0%25-red)

:::info Source
**File:** [`storage_manager.py`](./storage_manager.py) | **Line:** 338
:::

Open an overlay for searching and selecting a Drive folder.

## Purpose

Provides a comprehensive UI to browse, search, or paste a link to select a folder
            to serve as the LMS Root.

## Algorithm

- 1. List root folders.
  - 2. Build ListView of folders.
  - 3. Provide Search Bar (filters list).
  - 4. Provide "Paste Link" field (extracts ID).
  - 5. On Select: Save ID, Close Overlay, Reload Data.

## Interactions

- Lists files via `drive_service.list_files`.
- Searches via `drive_service.search_files`.
- calls `_save_lms_root` on selection.
