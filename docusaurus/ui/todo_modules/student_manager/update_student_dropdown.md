---
id: "update_student_dropdown"
sidebar_position: 4
title: "update_student_dropdown"
---

# ⚙️ update_student_dropdown

![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-0%25-red)

:::info Source
**File:** [`student_manager.py`](./student_manager.py) | **Line:** 64
:::

Refresh the student selection dropdown options.

## Purpose

Updates the main UI dropdown with the current list of registered students,
            formatting names to indicate bridging status, and ensuring the "Register" option exists.

## Algorithm

- 1. Clear existing options.
  - 2. Iterate through `todo.students`.
  - 3. If bridging, prefix name with `[B]`.
  - 4. Create dropdown Option objects.
  - 5. Prepend special `__register__` option.
  - 6. Trigger page update.

## Interactions

- Reads `todo.students`.
- Updates `todo.student_dropdown.options`.
- Updates `todo.page`.
