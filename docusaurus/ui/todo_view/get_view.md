---
id: "get_view"
sidebar_position: 15
title: "get_view"
---

# ⚙️ get_view

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`todo_view.py`](./todo_view.py) | **Line:** 1521
:::

Construct and return the complete TodoView UI layout.

Builds the entire LMS interface by assembling UI components into a
structured layout. Creates role-specific elements (forms, buttons)
based on current mode and arranges all components in a scrollable
column layout.

## Returns

**Type**: `ft.Column`

                Structure: Column[header, mode_controls, student_selector,
                form, divider, assignment_list]. Scrollable and expands to
                fill available space.

## Algorithm

- 1. **Display Initial Assignments**:
    - a. Call self.display_assignments()
    - b. Populates assignment_column with cards

  - 2. **Create Action Buttons**:
    - a. Create attach_btn ElevatedButton:
    - - Text: "📎 Attach File"
    - - on_click: pick_file
    - - icon: ATTACH_FILE
    - b. Create pick_deadline_btn ElevatedButton:
    - - Text: "📅 Set Deadline"
    - - on_click: open date_picker
    - - icon: CALENDAR_MONTH
    - c. Create add_btn ElevatedButton:
    - - Text: "➕ Add Assignment"
    - - on_click: assignment_manager.add_assignment
    - - icon: ADD
    - - style: blue background, white text

  - 3. **Build Assignment Form Container**:
    - a. Create form_container Container with:
    - i. Column containing:
    - - Text("Create New Assignment", size 20, bold)
    - - assignment_title field
    - - Row[subject_dropdown, max_score_field, target_dropdown]
    - - assignment_description field
    - - Row[Drive folder display and picker]
    - - Row[attach_btn, attachment_text]
    - - Row[pick_deadline_btn, deadline_display]
    - - Spacing container
    - - add_btn
    - ii. padding=20, border_radius=10
    - iii. bgcolor=light blue-grey (0.05 opacity)
    - b. Set visible based on current_mode == "teacher"
    - c. Store in self.form_container

  - 4. **Create Back Button** (if on_back provided):
    - a. If self.on_back exists:
    - i. Create IconButton with ARROW_BACK icon
    - ii. on_click: lambda e: on_back()
    - iii. tooltip: "Back to Dashboard"
    - b. Else:
    - i. Create empty Container

  - 5. **Create Manage Students Button**:
    - a. Create ElevatedButton:
    - - Text: "👥 Manage Students"
    - - on_click: student_manager.manage_students_dialog
    - - icon: PEOPLE
    - b. Set visible based on current_mode == "teacher"
    - c. Store in self.manage_students_btn

  - 6. **Build Header Section**:
    - a. Create Container with Row containing:
    - i. back_btn (if available)
    - ii. Icon(SCHOOL, size 40, blue)
    - iii. Text("Learning Management System", size 28, bold)
    - b. Set padding=20

  - 7. **Build Mode Controls Section**:
    - a. Create Container with Row containing:
    - i. mode_label (Teacher/Student View)
    - ii. mode_switch (toggle control)
    - iii. settings_btn (Storage button)
    - iv. Expanded container (pushes next item right)
    - v. manage_students_btn (teacher only)
    - b. Set padding=10, light blue background, border_radius=10

  - 8. **Build Assignment List Section**:
    - a. Create Container with Column containing:
    - i. Row with:
    - - Text("Assignments", size 20, bold, expand)
    - - filter_dropdown
    - ii. Container with assignment_column (expand=True)
    - b. Set expand=True for vertical fill

  - 9. **Assemble Complete Layout**:
    - a. Create root Column with:
    - i. Header container
    - ii. Mode controls container
    - iii. student_selector_row (student mode only)
    - iv. form_container (teacher mode only)
    - v. Divider (height=20)
    - vi. Assignment list container (expanded)
    - b. Set expand=True, scroll="auto"

  - 10. **Return Layout**:
    - a. Return assembled Column control

## Interactions

- **display_assignments()**: Populates assignment list
- **assignment_manager.add_assignment**: Creates new assignment
- **student_manager.manage_students_dialog**: Opens student management
- **storage_manager.open_new_assignment_folder_picker**: Opens folder picker
- **pick_file()**: Opens file picker
- **page.open()**: Opens date/time pickers

## Example

```python
# Build and display view
layout = todo_view.get_view()
page.add(layout)
page.update()

# Layout structure:
# ┌─ Header ──────────────────────┐
# │ ← [School Icon] LMS           │
# ├─ Mode Controls ───────────────┤
# │ 👨‍🏫 Teacher View [Toggle] Storage │
# ├─ Assignment Form ─────────────┤
# │ Create New Assignment         │
# │ [Title Field]                 │
# │ [Subject] [Score] [Target]    │
# │ [Description]                 │
# │ [📎 Attach] [📅 Deadline]      │
# │ [➕ Add Assignment]            │
# ├─ Assignment List ─────────────┤
# │ Assignments      [Filter]     │
# │ [Assignment Card 1]           │
# │ [Assignment Card 2]           │
# └───────────────────────────────┘
```

## See Also

- `__init__()`: Initializes components used in layout
- `_init_ui_components()`: Creates UI controls
- `display_assignments()`: Populates assignment list
- `switch_mode()`: Handles mode changes

## Notes

- Layout is scrollable (handles long content)
- Form visible only in teacher mode
- Student selector visible only in student mode
- Back button conditional on on_back callback
- All components created in _init_ui_components
- Assignment column populated by display_assignments
- Layout expands to fill available vertical space
- Responsive design with proper spacing
