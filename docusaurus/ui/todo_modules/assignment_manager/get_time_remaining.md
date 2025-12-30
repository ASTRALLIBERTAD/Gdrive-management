---
id: "get_time_remaining"
sidebar_position: 12
title: "get_time_remaining"
---

# ⚙️ get_time_remaining

![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`assignment_manager.py`](./assignment_manager.py) | **Line:** 789
:::

Calculate and format the time remaining until a deadline.

## Purpose

Provides a human-readable countdown string (e.g., "2d 5h remaining").

## Parameters

- **`deadline_str`** (str): ISO formatted deadline string.

## Returns

**Type**: `str`


## Algorithm

- 1. Parse ISO string to datetime.
  - 2. Compare with `now`.
  - 3. If past -> Return "Overdue".
  - 4. Calculate delta (days, hours, minutes).
  - 5. Return formatted string.
