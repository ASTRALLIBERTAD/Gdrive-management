---
id: "on_date_selected"
sidebar_position: 7
title: "on_date_selected"
---

# ⚙️ on_date_selected

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`todo_view.py`](./todo_view.py) | **Line:** 810
:::

Handle date picker selection event.

Updates the selected date value, refreshes the deadline display,
closes the date picker, and immediately opens the time picker for
completing the deadline selection.

## Parameters

- **`e`** (ft.ControlEvent): Date picker change event. Not used directly but required by Flet event handler signature.

## Returns

**Type**: `None`


## Algorithm

- 1. **Store Selected Date**:
    - a. Access self.date_picker.value (datetime.date object)
    - b. Assign to self.selected_date_value

  - 2. **Update Display**:
    - a. Call self.update_deadline_display()
    - b. Updates selected_deadline_display text with new date

  - 3. **Close Date Picker**:
    - a. Call self.page.close(self.date_picker)
    - b. Removes date picker from page overlay

  - 4. **Open Time Picker**:
    - a. Call self.page.open(self.time_picker)
    - b. Adds time picker to page overlay
    - c. User continues deadline selection with time

  - 5. **Refresh UI**:
    - a. Call self.page.update()
    - b. Renders all changes

## Interactions

- **ft.DatePicker**: Reads selected value
- **update_deadline_display()**: Updates display text
- **ft.Page**: Closes date picker, opens time picker

## Example

```python
# User selects December 31, 2025
todo_view.on_date_selected(event)
# selected_date_value = date(2025, 12, 31)
# Display: "Deadline: 2025-12-31"
# Date picker closes
# Time picker opens
```

## See Also

- `on_time_selected()`: Handles time selection
- `update_deadline_display()`: Updates deadline text
- `date_picker`: Date picker control
- `time_picker`: Time picker control

## Notes

- Part of two-step deadline selection process
- Date picker auto-closes after selection
- Time picker auto-opens for seamless UX
- Event parameter required but unused
- Display updates immediately
