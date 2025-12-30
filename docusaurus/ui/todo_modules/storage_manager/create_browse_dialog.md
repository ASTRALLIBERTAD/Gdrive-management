---
id: "create_browse_dialog"
sidebar_position: 12
title: "create_browse_dialog"
---

# ⚙️ create_browse_dialog

![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-20%25-red)

:::info Source
**File:** [`storage_manager.py`](./storage_manager.py) | **Line:** 485
:::

Open an overlay to browse and select a Drive folder.

## Purpose

A reusable file browser dialog that allows traversing the Drive folder hierarchy
            to select a specific destination (e.g., for assignment submissions).

## Parameters

- **`initial_parent_id`** (str): Starting folder ID (or 'root').
- **`on_select`** (Callable): Callback function `fn(selected_id)` to execute on selection.

## Algorithm

- 1. `load_folder(id)`: Fetch children folders.
  - 2. Display "Up" button if not root.
  - 3. Display children as click-to-enter tiles.
  - 4. "Select Current Folder" button returns current ID.
  - 5. Checkmark icon on tile returns that specific folder's ID.

## Interactions

- Calls `drive_service.list_files` (recursive navigation).
- Updates UI dynamic list.
