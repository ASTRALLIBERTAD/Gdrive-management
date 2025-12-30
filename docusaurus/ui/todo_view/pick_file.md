---
id: "pick_file"
sidebar_position: 10
title: "pick_file"
---

# ⚙️ pick_file

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`todo_view.py`](./todo_view.py) | **Line:** 1006
:::

Open file picker dialog for attaching a local file to assignment.

Creates and displays a file picker dialog, captures the selected file
path and name, and updates the attachment display text.

## Parameters

- **`e`** (ft.ControlEvent): Button click event. Not used directly but required by Flet event handler signature.

## Returns

**Type**: `None`


## Algorithm

- 1. **Define Result Callback**:
    - a. Define inner function on_result(e: FilePickerResultEvent)
    - b. Callback executes when user selects file
    - c. Implementation:
    - i. Check if e.files is not empty
    - ii. If files selected:
    - - Store e.files[0].path in selected_attachment["path"]
    - - Store e.files[0].name in selected_attachment["name"]
    - - Update attachment_text.value = "📎 &#123;filename&#125;"
    - - Call page.update() to render changes

  - 2. **Create File Picker**:
    - a. Instantiate ft.FilePicker(on_result=on_result)
    - b. File picker configured with result callback

  - 3. **Add to Page Overlay**:
    - a. Append file_picker to page.overlay list
    - b. Makes picker available for display

  - 4. **Update Page**:
    - a. Call page.update() to register picker

  - 5. **Show File Picker**:
    - a. Call file_picker.pick_files()
    - b. Opens system file selection dialog
    - c. User selects file
    - d. on_result callback executes with selection

## Interactions

- **ft.FilePicker**: Creates and displays file selection dialog
- **ft.Page.overlay**: Registers picker with page
- **selected_attachment**: Updates with file info
- **attachment_text**: Updates display text

## Example

```python
# User clicks "Attach File" button
todo_view.pick_file(click_event)
# File picker opens
# User selects "homework.pdf"
print(todo_view.selected_attachment)
# {'path': '/path/to/homework.pdf', 'name': 'homework.pdf'}
print(todo_view.attachment_text.value)
# 📎 homework.pdf
```

## See Also

- `get_view()`: Creates "Attach File" button
- `ft.FilePicker`: Flet file picker component

## Notes

- File picker opens system-native dialog
- Only one file can be selected at a time
- File not uploaded until assignment created
- Attachment info stored in selected_attachment dict
- Display text shows file name with paperclip emoji
- Event parameter required but unused
