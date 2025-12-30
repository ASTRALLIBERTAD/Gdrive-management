---
id: "show_past_deadline_dialog"
sidebar_position: 5
title: "show_past_deadline_dialog"
---

# ⚙️ show_past_deadline_dialog

![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-20%25-red)

:::info Source
**File:** [`assignment_manager.py`](./assignment_manager.py) | **Line:** 219
:::

Display a warning dialog if the selected deadline is in the past.

## Purpose

Alerts the teacher that the selected date/time is invalid for a deadline.

## Parameters

- **`deadline`** (datetime): The selected deadline.
- **`current_time`** (datetime): Current system time.

## Algorithm

- 1. Format deadline and current time strings.
  - 2. Build AlertDialog with red warning icon.
  - 3. Display comparison of Selected vs Current time.
  - 4. Set `page.dialog = dialog` and open.

## Interactions

- Shows `ft.AlertDialog`.
- Updates `todo.page`.
