---
id: "delete_saved_link"
sidebar_position: 7
title: "delete_saved_link"
---

# ⚙️ delete_saved_link

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`paste_links_manager.py`](./paste_links_manager.py) | **Line:** 554
:::

Remove specific Drive link from saved history.

Deletes link matching provided item's ID from saved links list,
saves updated list, and refreshes view if currently active.

## Parameters

- **`item`** (dict): Link item to remove. Must contain 'id' key for matching. Other keys (name, mimeType, url) ignored for deletion but typically present.

## Returns

**Type**: `None`


## Algorithm

- 1. **Load Current Links**:
    - a. Call self.load_saved_links()
    - b. Returns list of all saved links

  - 2. **Filter Out Item**:
    - a. Use list comprehension
    - b. Keep links where ID doesn't match item's ID
    - c. Expression: [l for l in links if l.get("id") != item.get("id")]
    - d. Creates new list without deleted item

  - 3. **Save Updated List**:
    - a. Call self.save_saved_links(links)
    - b. Persists filtered list to JSON

  - 4. **Refresh View** (if active):
    - a. Check if dash.current_view == "paste_links"
    - b. If yes (paste links view is active):
    - i. Call self.load_paste_links_view()
    - ii. Refreshes UI to show updated list
    - c. If no (different view active):
    - i. No refresh needed (silent update)

## Interactions

- **load_saved_links()**: Retrieves current list
- **save_saved_links()**: Persists filtered list
- **load_paste_links_view()**: Refreshes UI

## Example

```python
# Delete saved link
saved_links = paste_manager.load_saved_links()
item_to_delete = saved_links[0]
print(item_to_delete)
# {'id': 'abc123', 'name': 'Old Folder', 'mimeType': '...', 'url': '...'}

paste_manager.delete_saved_link(item_to_delete)
# Link removed from storage
# View refreshed if currently displayed

# Verify deletion
updated_links = paste_manager.load_saved_links()
print(len(updated_links))
# # One less than before

# Delete from different view
dashboard.current_view = "your_folders"
paste_manager.delete_saved_link(item_to_delete)
# Link deleted but no view refresh (not active)
```

## See Also

- `load_saved_links()`: Retrieves links
- `save_saved_links()`: Persists changes
- `load_paste_links_view()`: Refreshes view
- `build_saved_links_ui()`: Creates delete buttons

## Notes

- Deletes by ID match (exact)
- Safe if item doesn't exist (no error)
- Refreshes view only if currently active
- Immediate persistence to JSON
- Called from delete button in UI
