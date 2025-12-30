---
id: "on_student_selected"
sidebar_position: 13
title: "on_student_selected"
---

# ⚙️ on_student_selected

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`todo_view.py`](./todo_view.py) | **Line:** 1268
:::

Handle student selection change in student dropdown.

Processes student dropdown selection, triggering registration dialog
if the special registration option is selected, or updating the current
student and refreshing the assignment display.

## Parameters

- **`e`** (ft.ControlEvent): Dropdown change event. Not used directly but required by Flet event handler signature.

## Returns

**Type**: `None`


## Algorithm

- 1. **Check for Registration Option**:
    - a. If student_dropdown.value == "__register__":
    - i. Set student_dropdown.value = None (clear selection)
    - ii. Call student_manager.register_student_dialog()
    - iii. Opens dialog for new student registration
    - iv. Return early (exit function)

  - 2. **Update Current Student**:
    - a. Assign student_dropdown.value to current_student_email
    - b. Stores selected student's email

  - 3. **Refresh Assignment Display**:
    - a. Call self.display_assignments()
    - b. Shows assignments for newly selected student

## Interactions

- **student_dropdown**: Reads selected value
- **student_manager.register_student_dialog()**: Opens registration
- **current_student_email**: Updates with selection
- **display_assignments()**: Refreshes display

## Example

```python
# User selects a student
todo_view.student_dropdown.value = "student@example.com"
todo_view.on_student_selected(event)
print(todo_view.current_student_email)
# student@example.com
# Assignments refresh to show student's work

# User selects registration option
todo_view.student_dropdown.value = "__register__"
todo_view.on_student_selected(event)
# Registration dialog opens
print(todo_view.student_dropdown.value)
# None
```

## See Also

- `StudentManager`: Handles registration
- `display_assignments()`: Refreshes assignment list
- `student_dropdown`: Student selector control

## Notes

- Special value "__register__" triggers registration dialog
- Dropdown cleared after selecting registration option
- current_student_email used by display_assignments to filter
- Event parameter required but unused
