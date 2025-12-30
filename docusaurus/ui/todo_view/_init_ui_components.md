---
id: "_init_ui_components"
sidebar_position: 4
title: "_init_ui_components"
---

# ⚙️ _init_ui_components

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`todo_view.py`](./todo_view.py) | **Line:** 418
:::

Initialize all persistent UI controls and layout containers.

Creates and configures every UI component used by TodoView including
input fields, dropdowns, pickers, display texts, buttons, and layout
containers. Stores all components as instance attributes for later
access and modification. Does not attach components to page; assembly
happens in get_view().

## Returns

**Type**: `None`


## Algorithm

- 1. **Create Input Fields**:
    - a. Create assignment_title TextField (hint: "Assignment Title")
    - b. Create assignment_description TextField:
    - - Multiline: True
    - - Min lines: 3, max lines: 5
    - - Hint: "Description/Instructions"
    - c. Create max_score_field TextField:
    - - Width: 150px
    - - Keyboard type: NUMBER
    - - Input filter: NumbersOnlyInputFilter

  - 2. **Create Dropdown Selectors**:
    - a. Create subject_dropdown with options:
    - - Mathematics, Science, English, History
    - - Computer Science, Arts, Physical Education, Other
    - - Width: 200px
    - b. Create target_dropdown with options:
    - - "all" -> "All Students"
    - - "bridging" -> "Bridging Only"
    - - "regular" -> "Regular Only"
    - - Default value: "all", width: 200px
    - c. Create filter_dropdown with options:
    - - All, Active, Completed, Overdue
    - - Default: "All", width: 150px
    - - on_change: lambda e: display_assignments()
    - d. Create student_dropdown:
    - - Width: 250px
    - - on_change: on_student_selected
    - - Populated by student_manager

  - 3. **Initialize Drive Folder Selection**:
    - a. Set selected_drive_folder_id = None
    - b. Create drive_folder_label Text:
    - - Value: "No folder selected"
    - - Size: 12px, italic: True

  - 4. **Initialize File Attachment**:
    - a. Create attachment_text Text:
    - - Value: "No file attached"
    - - Size: 12px, italic: True
    - b. Create selected_attachment dict:
    - - Keys: "path", "name"
    - - Initial values: None

  - 5. **Initialize Deadline Selection**:
    - a. Set selected_date_value = None
    - b. Set selected_time_value = None
    - c. Create selected_deadline_display Text:
    - - Value: "No deadline selected"
    - - Size: 12px, italic: True
    - d. Create date_picker DatePicker:
    - - on_change: on_date_selected
    - e. Create time_picker TimePicker:
    - - on_change: on_time_selected

  - 6. **Create Layout Containers**:
    - a. Create assignment_column Column:
    - - Scroll: "auto", expand: True
    - - Spacing: 10px
    - - Will hold assignment cards

  - 7. **Create Mode Controls**:
    - a. Create mode_switch Switch:
    - - Value: False (teacher mode)
    - - on_change: switch_mode
    - b. Create mode_label Text:
    - - Value: "👨‍🏫 Teacher View"
    - - Size: 16px, weight: BOLD

  - 8. **Create Action Buttons**:
    - a. Create settings_btn ElevatedButton:
    - - Text: "Storage"
    - - Icon: SETTINGS
    - - on_click: storage_manager.show_storage_settings

  - 9. **Create Student Selector Row**:
    - a. Create student_selector_row Row:
    - - Contains: Text("Viewing as:"), student_dropdown
    - - Visible: False (only in student mode)
    - b. Call student_manager.update_student_dropdown():
    - - Populates dropdown with student emails

  - 10. **Initialize Containers** (created later in get_view):
    - a. Set form_container = None (created in get_view)
    - b. Set manage_students_btn = None (created in get_view)

## Interactions

- **ft.TextField, ft.Dropdown, ft.DatePicker, etc.**: UI component creation
- **student_manager.update_student_dropdown()**: Populates student dropdown
- **Event handlers**: Registered for dropdowns, switch, pickers

## Example

```python
# After initialization
todo = TodoView(page, callback, drive)
# All components created and stored
print(todo.assignment_title.hint_text)
# Assignment Title
print(len(todo.subject_dropdown.options))
# 8
print(todo.mode_switch.value)
# False
print(todo.assignment_column.scroll)
# auto
```

## See Also

- `__init__()`: Calls this during initialization
- `get_view()`: Assembles components into layout
- `switch_mode()`: Handles mode switch events
- `display_assignments()`: Updates assignment_column

## Notes

- Components created but not attached to page yet
- All components stored as instance attributes
- Event handlers registered during creation
- Dropdowns populated with predefined options
- Student dropdown populated by student_manager
- Form and manage button containers created later
- Assignment column initially empty (populated by display_assignments)
- Picker controls added to page overlay when needed
