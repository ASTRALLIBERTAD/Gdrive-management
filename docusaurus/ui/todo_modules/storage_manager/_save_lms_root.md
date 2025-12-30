---
id: "_save_lms_root"
sidebar_position: 11
title: "_save_lms_root"
---

# ⚙️ _save_lms_root

![Completeness](https://img.shields.io/badge/Docs-20%25-red)

:::info Source
**File:** [`storage_manager.py`](./storage_manager.py) | **Line:** 455
:::

Update and persist the LMS root folder ID in local config.

## Purpose

Saves the selected folder ID to `lms_config.json` so it persists across restarts.

## Parameters

- **`folder_id`** (str): The Drive folder ID.

## Interactions

- Writes to `lms_config.json`.
- Updates in-memory `todo.data_manager.lms_root_id`.
