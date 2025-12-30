---
id: "close_preview"
sidebar_position: 18
title: "close_preview"
---

# ⚙️ close_preview

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`file_preview_service.py`](./file_preview_service.py) | **Line:** 1628
:::

Close currently displayed preview overlay.

Removes preview overlay from page and cleans up references.
Safe to call even if no preview is active.

## Returns

**Type**: `None`


## Algorithm

- 1. **Check Overlay Exists**:
    - a. If current_overlay is None, return early
    - b. If current_overlay not in page.overlay, return early

  - 2. **Remove Overlay**:
    - a. Call page.overlay.remove(current_overlay)
    - b. Removes from overlay list

  - 3. **Clear Reference**:
    - a. Set current_overlay = None
    - b. Prevents dangling reference

  - 4. **Update Page**:
    - a. Call page.update()
    - b. Renders removal

## Interactions

- **page.overlay**: Overlay list management
- **page.update()**: UI refresh

## Example

```python
# Close active preview
preview_service.show_preview(file_path='file.txt')
# Preview displayed
preview_service.close_preview()
# Preview removed

# Safe to call when no preview
preview_service.close_preview()
# No error, no action
```

## See Also

- `show_preview()`: Opens preview (registers close button)

## Notes

- Safe to call multiple times
- No error if no active preview
- Clears overlay reference
- User can also close via close button in overlay
- Removes entire overlay from page
