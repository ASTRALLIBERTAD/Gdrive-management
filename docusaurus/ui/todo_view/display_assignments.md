---
id: "display_assignments"
sidebar_position: 11
title: "display_assignments"
---

# ⚙️ display_assignments

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`todo_view.py`](./todo_view.py) | **Line:** 1088
:::

Render the list of assignments based on current mode and filters.

Clears the assignment column and delegates rendering to the appropriate
manager method based on whether the user is in teacher or student mode.

## Returns

**Type**: `None`


## Algorithm

- 1. **Clear Assignment Display**:
    - a. Access self.assignment_column.controls
    - b. Call clear() to remove all existing cards

  - 2. **Check Current Mode**:
    - a. If self.current_mode == "teacher":
    - i. Call assignment_manager.display_teacher_view()
    - ii. Manager shows all assignments with edit/delete
    - b. Else (student mode):
    - i. Call assignment_manager.display_student_view()
    - ii. Manager shows assigned assignments with submit buttons

  - 3. **Refresh UI**:
    - a. Call self.page.update()
    - b. Renders updated assignment_column

## Interactions

- **assignment_column**: Clears controls list
- **AssignmentManager.display_teacher_view()**: Renders teacher view
- **AssignmentManager.display_student_view()**: Renders student view
- **ft.Page.update()**: Renders changes

## Example

```python
# Display in teacher mode
todo_view.current_mode = "teacher"
todo_view.display_assignments()
# Shows all assignments with edit/delete buttons

# Display in student mode
todo_view.current_mode = "student"
todo_view.current_student_email = "student@example.com"
todo_view.display_assignments()
# Shows assignments for selected student with submit buttons
```

## See Also

- `switch_mode()`: Calls this after mode change
- `AssignmentManager`: Handles rendering
- `assignment_column`: Container for assignment cards

## Notes

- Called automatically after mode switch
- Called after filter dropdown change
- Delegation pattern - manager handles actual rendering
- Assignment column cleared before repopulation
- Manager accesses self.assignments for data
- Manager creates assignment cards dynamically
