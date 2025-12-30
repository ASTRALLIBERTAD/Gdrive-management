---
id: "upload_assignment_attachment"
sidebar_position: 5
title: "upload_assignment_attachment"
---

# ⚙️ upload_assignment_attachment

![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`storage_manager.py`](./storage_manager.py) | **Line:** 132
:::

Upload an attachment file to the subject's 'Attachments' subfolder.

## Purpose

Organizes assignment files by placing them into a specific 'Attachments' subdirectory
            under the relevant Subject folder.

## Parameters

- **`file_path`** (str): Local path to the file to upload.
- **`file_name`** (str): Desired filename in Drive.
- **`subject`** (str): The subject this assignment belongs to.
- **`assignment_id`** (str): Assignment ID used to prefix the filename for uniqueness.

## Returns

**Type**: `dict | None`


## Algorithm

- 1. Get ID for Subject folder.
  - 2. Get ID for 'Attachments' subfolder within Subject folder.
  - 3. Construct prefixed filename: `ATTACH_&#123;id&#125;_&#123;name&#125;`.
  - 4. Upload file to 'Attachments' folder.

## Interactions

- Calls `get_or_create_subject_folder_in_lms`.
- Calls `_get_or_create_attachments_folder_in_lms`.
- Calls `drive_service.upload_file`.
