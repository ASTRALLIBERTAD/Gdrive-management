---
id: "_validate_email"
sidebar_position: 7
title: "_validate_email"
---

# ⚙️ _validate_email

![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`student_manager.py`](./student_manager.py) | **Line:** 299
:::

Validate email format and uniqueness.

## Purpose

Checks if the provided email string is a valid format and is not already in use.

## Parameters

- **`email`** (str): Email to validate.

## Returns

**Type**: `tuple[bool, str]`


## Algorithm

- 1. Check empty string.
  - 2. Check for '@' and '.'.
  - 3. Iterate students to check for duplicates.
  - 4. Return result tuple.

## Interactions

- reads `todo.students`.
