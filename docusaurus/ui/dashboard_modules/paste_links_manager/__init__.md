---
id: "__init__"
sidebar_position: 3
title: "__init__"
---

# 🔧 __init__

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`paste_links_manager.py`](./paste_links_manager.py) | **Line:** 210
:::

Initialize PasteLinksManager with Dashboard and preview service.

Sets up link management capabilities by storing Dashboard reference
and initializing FilePreviewService. Handles import failure gracefully.

## Parameters

- **`dashboard`** (Dashboard): Parent Dashboard instance providing access to: - page: Flet page for updates - drive: DriveService for link resolution - folder_navigator: For folder navigation - file_manager: For file info display - paste_link_field: Input control for URLs - current_view: View state tracking

## Algorithm

- 1. **Store Dashboard Reference**:
    - a. Assign dashboard parameter to self.dash
    - b. All Dashboard services accessed via dash

  - 2. **Initialize Preview Service**:
    - a. Enter try block for graceful failure
    - b. Import FilePreviewService from services module
    - c. Instantiate with dashboard.page and dashboard.drive
    - d. Store in self.file_preview

  - 3. **Handle Import Failure**:
    - a. Catch ImportError if service unavailable
    - b. Set self.file_preview = None
    - c. Preview disabled, falls back to file info
    - d. No error raised (graceful degradation)

## Interactions

- **Dashboard**: Stores reference
- **FilePreviewService**: Initializes if available

## Example

```python
# Standard initialization
dashboard = Dashboard(page, auth_service)
paste_manager = PasteLinksManager(dashboard)
print(paste_manager.file_preview)
# <FilePreviewService instance>

# Preview service unavailable
paste_manager = PasteLinksManager(dashboard)
print(paste_manager.file_preview)
# None
# Manager still functional, uses file info
```

## See Also

- `Dashboard`: Parent container
- `FilePreviewService`: Preview service

## Notes

- Dashboard must be initialized first
- Preview service optional (graceful degradation)
- No exceptions raised on initialization
- file_preview checked before use
