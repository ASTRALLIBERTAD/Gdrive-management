---
id: "switch_mode"
sidebar_position: 12
title: "switch_mode"
---

# ⚙️ switch_mode

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`todo_view.py`](./todo_view.py) | **Line:** 1154
:::

Toggle between Teacher and Student view modes.

Switches the application mode based on the mode switch control,
updates UI element visibility for role-specific features, and
refreshes the assignment display.

## Parameters

- **`e`** (ft.ControlEvent): Switch toggle event. Not used directly but required by Flet event handler signature.

## Returns

**Type**: `None`


## Algorithm

- 1. **Update Mode State**:
    - a. Check self.mode_switch.value (True/False)
    - b. If True:
    - i. Set self.current_mode = "student"
    - c. If False:
    - i. Set self.current_mode = "teacher"

  - 2. **Configure Student Mode** (if student):
    - a. Set mode_label.value = "👨‍🎓 Student View"
    - b. Set student_selector_row.visible = True
    - - Shows student dropdown
    - c. If form_container exists:
    - i. Set form_container.visible = False
    - ii. Hides assignment creation form
    - d. If manage_students_btn exists:
    - i. Set manage_students_btn.visible = False
    - ii. Hides student management button

  - 3. **Configure Teacher Mode** (else teacher):
    - a. Set mode_label.value = "👨‍🏫 Teacher View"
    - b. Set student_selector_row.visible = False
    - - Hides student dropdown
    - c. If form_container exists:
    - i. Set form_container.visible = True
    - ii. Shows assignment creation form
    - d. If manage_students_btn exists:
    - i. Set manage_students_btn.visible = True
    - ii. Shows student management button

  - 4. **Refresh Assignment Display**:
    - a. Call self.display_assignments()
    - b. Updates assignment list for current mode

  - 5. **Update Page**:
    - a. Call self.page.update()
    - b. Renders all visibility changes

## Interactions

- **mode_switch**: Reads toggle value
- **mode_label**: Updates text and emoji
- **student_selector_row**: Shows/hides student selector
- **form_container**: Shows/hides assignment form
- **manage_students_btn**: Shows/hides management button
- **display_assignments()**: Refreshes assignment list

## Example

```python
# Switch to student mode
todo_view.mode_switch.value = True
todo_view.switch_mode(event)
print(todo_view.current_mode)
# student
print(todo_view.mode_label.value)
# 👨‍🎓 Student View
print(todo_view.student_selector_row.visible)
# True
print(todo_view.form_container.visible)
# False

# Switch back to teacher mode
todo_view.mode_switch.value = False
todo_view.switch_mode(event)
print(todo_view.current_mode)
# teacher
print(todo_view.mode_label.value)
# 👨‍🏫 Teacher View
print(todo_view.form_container.visible)
# True
```

## See Also

- `display_assignments()`: Refreshes display after switch
- `on_student_selected()`: Handles student selection in student mode
- `mode_switch`: Switch control

## Notes

- Mode switch control is a toggle (True/False)
- Student mode: read-only view of assigned work
- Teacher mode: full CRUD operations on assignments
- UI elements show/hide based on mode
- Assignment display updates automatically
- Event parameter required but unused
