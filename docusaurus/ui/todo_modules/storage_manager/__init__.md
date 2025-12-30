---
id: "__init__"
sidebar_position: 3
title: "__init__"
---

# 🔧 __init__

![Completeness](https://img.shields.io/badge/Docs-20%25-red)

:::info Source
**File:** [`storage_manager.py`](./storage_manager.py) | **Line:** 54
:::

Initialize the StorageManager.

## Purpose

Sets up the storage manager with necessary service references and initializes the cache.

## Parameters

- **`todo_view`** (TodoView): Parent view instance for accessing global state.
- **`drive_service`** (DriveService): Service instance for Drive API operations.

## Interactions

- Stores references to `todo_view` and `drive_service`.
- Initializes `subject_folders_cache` as empty dict.
