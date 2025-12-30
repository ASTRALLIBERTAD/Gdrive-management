---
id: "upload_submission_to_link_drive"
sidebar_position: 7
title: "upload_submission_to_link_drive"
---

# ⚙️ upload_submission_to_link_drive

![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`storage_manager.py`](./storage_manager.py) | **Line:** 212
:::

Upload a student submission to a specific Drive folder.

## Purpose

Handles the upload of student work to a designated assignment folder (linked folder).

## Parameters

- **`file_path`** (str): Local path to the submission file.
- **`file_name`** (str): Original filename.
- **`subject`** (str): Subject name (for context/logging).
- **`student_name`** (str): Name of the student (for file prefixing).
- **`link_drive_id`** (str): The target Drive Folder ID where submissions go.

## Returns

**Type**: `dict | None`


## Algorithm

- 1. Verify Drive Service and Target Folder ID.
  - 2. Construct filename: `&#123;student_name&#125;_&#123;file_name&#125;`.
  - 3. Upload to `link_drive_id`.

## Interactions

- Calls `drive_service.upload_file`.
