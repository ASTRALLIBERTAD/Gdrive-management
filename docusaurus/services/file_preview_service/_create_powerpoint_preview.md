---
id: "_create_powerpoint_preview"
sidebar_position: 13
title: "_create_powerpoint_preview"
---

# ⚙️ _create_powerpoint_preview

![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`file_preview_service.py`](./file_preview_service.py) | **Line:** 1236
:::

Create Microsoft PowerPoint placeholder with download and browser options.

Shows PowerPoint icon and metadata. No inline presentation viewer.

## Parameters

- **`file_data`** (bytes): PowerPoint file binary content (.ppt or .pptx).
- **`file_name`** (str): Presentation filename for display and download.
- **`size_mb`** (float): File size in megabytes.
- **`file_id`** (str or None): Drive file ID for browser viewing.

## Returns

**Type**: `ft.Column`


## Algorithm

- Similar to _create_word_preview but with:
  - - ORANGE SLIDESHOW icon
  - - Title: "Presentation Document"
  - - Download button: "Download Presentation"
  - - ORANGE Open button color

## See Also

- `_create_word_preview()`: Similar structure

## Notes

- Supports both .ppt and .pptx
- ORANGE icon (standard PowerPoint color)
- No inline slide viewer
