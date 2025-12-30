---
id: "get_or_create_subject_folder_in_lms"
sidebar_position: 4
title: "get_or_create_subject_folder_in_lms"
---

# ⚙️ get_or_create_subject_folder_in_lms

![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`storage_manager.py`](./storage_manager.py) | **Line:** 72
:::

Retrieve or create a folder for a specific subject within the LMS root.

## Purpose

Ensures a dedicated folder exists for the given subject to organize files.
            Utilizes caching to prevent redundant API calls for the same subject.

## Parameters

- **`subject`** (str): Name of the subject (e.g., 'Mathematics').

## Returns

**Type**: `str | None`


## Algorithm

- 1. Check if Drive Service and LMS Root are configured.
  - 2. Check `subject_folders_cache` for existing ID.
  - 3. If cached, verify validity (optional) and return.
  - 4. If not cached:
    - a. List files in LMS Root filtering by name=`subject`.
    - b. If found, update cache and return ID.
    - c. If not found, create new folder, update cache, and return ID.

## Interactions

- Reads `todo.data_manager.lms_root_id`.
- Calls `drive_service.list_files` (to find existing).
- Calls `drive_service.create_folder` (if missing).
