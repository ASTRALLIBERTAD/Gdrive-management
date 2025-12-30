---
id: "on_time_selected"
sidebar_position: 8
title: "on_time_selected"
---

# ⚙️ on_time_selected

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`todo_view.py`](./todo_view.py) | **Line:** 878
:::

Handle time picker selection event.

Updates the selected time value, refreshes the deadline display,
and closes the time picker to complete the deadline selection process.

## Parameters

- **`e`** (ft.ControlEvent): Time picker change event. Not used directly but required by Flet event handler signature.

## Returns

**Type**: `None`


## Algorithm

- 1. **Store Selected Time**:
    - a. Access self.time_picker.value (datetime.time object)
    - b. Assign to self.selected_time_value

  - 2. **Update Display**:
    - a. Call self.update_deadline_display()
    - b. Updates selected_deadline_display with date and time

  - 3. **Close Time Picker**:
    - a. Call self.page.close(self.time_picker)
    - b. Removes time picker from page overlay

  - 4. **Refresh UI**:
    - a. Call self.page.update()
    - b. Renders all changes

## Interactions

- **ft.TimePicker**: Reads selected value
- **update_deadline_display()**: Updates display text
- **ft.Page**: Closes time picker, updates UI

## Example

```python
# User selects 11:59 PM
todo_view.on_time_selected(event)
# selected_time_value = time(23, 59)
# Display: "Deadline: 2025-12-31 at 23:59:00"
# Time picker closes
```

## See Also

- `on_date_selected()`: Handles date selection
- `update_deadline_display()`: Updates deadline text
- `time_picker`: Time picker control

## Notes

- Completes two-step deadline selection
- Time picker auto-closes after selection
- Display shows complete date and time
- Event parameter required but unused
