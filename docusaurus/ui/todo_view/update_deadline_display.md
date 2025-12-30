---
id: "update_deadline_display"
sidebar_position: 9
title: "update_deadline_display"
---

# ⚙️ update_deadline_display

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`todo_view.py`](./todo_view.py) | **Line:** 936
:::

Update the UI text showing the selected deadline.

Formats and displays the deadline based on currently selected
date and time values. Shows partial deadline if only date selected.

## Returns

**Type**: `None`


## Algorithm

- 1. **Check Both Values Available**:
    - a. If selected_date_value AND selected_time_value:
    - i. Format: "Deadline: &#123;date&#125; at &#123;time&#125;"
    - ii. Update selected_deadline_display.value
    - iii. Complete deadline shown

  - 2. **Check Only Date Available**:
    - a. Elif selected_date_value only:
    - i. Format: "Deadline: &#123;date&#125;"
    - ii. Update selected_deadline_display.value
    - iii. Time not yet selected

  - 3. **No Selection**:
    - a. Else (neither selected):
    - i. Set value: "No deadline selected"
    - ii. Default state

## Interactions

- **selected_date_value**: Reads date attribute
- **selected_time_value**: Reads time attribute
- **selected_deadline_display**: Updates text value

## Example

```python
# Both date and time selected
todo_view.selected_date_value = date(2025, 12, 31)
todo_view.selected_time_value = time(23, 59)
todo_view.update_deadline_display()
print(todo_view.selected_deadline_display.value)
# Deadline: 2025-12-31 at 23:59:00

# Only date selected
todo_view.selected_time_value = None
todo_view.update_deadline_display()
print(todo_view.selected_deadline_display.value)
# Deadline: 2025-12-31

# Nothing selected
todo_view.selected_date_value = None
todo_view.update_deadline_display()
print(todo_view.selected_deadline_display.value)
# No deadline selected
```

## See Also

- `on_date_selected()`: Calls this after date selection
- `on_time_selected()`: Calls this after time selection
- `selected_deadline_display`: Display text control

## Notes

- Called automatically after date/time picker selections
- Handles partial deadline (date only)
- Formats datetime objects as strings
- Display text automatically updates in UI
