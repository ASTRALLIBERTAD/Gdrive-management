---
id: "refresh_folder_contents"
sidebar_position: 7
title: "refresh_folder_contents"
---

# ⚙️ refresh_folder_contents

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`folder_navigator.py`](./folder_navigator.py) | **Line:** 674
:::

Force refresh of current folder view with cache invalidation.

Invalidates DriveService cache for current folder and reloads
contents without adding to history stack. Ensures fresh data
from Drive API.

## Returns

**Type**: `None`


## Algorithm

- 1. **Invalidate Cache**:
    - a. Call dash.drive._invalidate_cache(current_folder_id)
    - b. Removes cached data for current folder
    - c. Forces API call on next list_files

  - 2. **Reload Contents**:
    - a. Call show_folder_contents() with:
    - i. folder_id: dash.current_folder_id
    - ii. folder_name: dash.current_folder_name
    - iii. push_to_stack: False (no history entry)
    - b. Reloads same folder with fresh data

## Interactions

- **DriveService._invalidate_cache()**: Cache management
- **show_folder_contents()**: Reload display

## Example

```python
# User clicks Refresh button
navigator.refresh_folder_contents()
# Current folder reloaded with fresh data
# No duplicate in history stack

# After file upload
dashboard.drive.upload_file('file.pdf', current_folder_id)
navigator.refresh_folder_contents()
# Shows newly uploaded file
```

## See Also

- `show_folder_contents()`: Main navigation method
- `_invalidate_cache()`: Cache management

## Notes

- Always gets fresh data from API
- Does not add to history stack
- Useful after file operations (upload, delete)
- Called from refresh button in header
- Maintains current folder context
