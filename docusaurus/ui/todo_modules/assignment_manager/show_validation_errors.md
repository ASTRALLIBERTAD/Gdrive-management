---
id: "show_validation_errors"
sidebar_position: 6
title: "show_validation_errors"
---

# ⚙️ show_validation_errors

![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-20%25-red)

:::info Source
**File:** [`assignment_manager.py`](./assignment_manager.py) | **Line:** 285
:::

Display a dialog listing form validation errors.

## Purpose

Provides specific feedback on why assignment creation failed.

## Parameters

- **`errors`** (list[str]): List of error messages to display.

## Algorithm

- 1. Create a list of UI rows for each error message.
  - 2. Build AlertDialog showing all errors.
  - 3. Open dialog.
  - 4. Show summary via snackbar.

## Interactions

- Shows `ft.AlertDialog`.
- Calls `todo.show_snackbar`.
