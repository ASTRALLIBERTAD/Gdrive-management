---
id: "get_status"
sidebar_position: 13
title: "get_status"
---

# ⚙️ get_status

![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`assignment_manager.py`](./assignment_manager.py) | **Line:** 833
:::

Determine the status of an assignment.

## Purpose

Calculates whether an assignment is "Active", "Overdue", or "Completed".

## Parameters

- **`deadline_str`** (str): ISO formatted deadline.
- **`assignment_id`** (str, optional): Assignment ID (for checking submission status).

## Returns

**Type**: `str`


## Algorithm

- 1. If student mode: Check if submitted -> Return "Completed".
  - 2. If no deadline -> Return "Active".
  - 3. Compare deadline with current time.
  - 4. If past -> "Overdue".
  - 5. Else -> "Active".
