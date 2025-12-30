---
id: "studentmanager"
sidebar_position: 2
title: "StudentManager"
---

# 📦 StudentManager

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-20%25-red)

:::info Source
**File:** [`student_manager.py`](./student_manager.py) | **Line:** 18
:::

Manages student identities and registration.

## Attributes

- **`todo`** (TodoView): Reference to the main TodoView instance which holds the student list and global state.

## Examples

```python
manager = StudentManager(todo_view)
manager.update_student_dropdown()
regular_students = manager.get_regular_students()
```

## See Also

- `TodoView`
- `DataManager`
