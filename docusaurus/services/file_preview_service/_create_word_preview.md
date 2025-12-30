---
id: "_create_word_preview"
sidebar_position: 11
title: "_create_word_preview"
---

# ⚙️ _create_word_preview

![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`file_preview_service.py`](./file_preview_service.py) | **Line:** 1120
:::

Create Microsoft Word placeholder with download and browser options.

Shows Word icon and metadata. No inline Word viewer (requires external
application or browser).

## Parameters

- **`file_data`** (bytes): Word document binary content (.doc or .docx).
- **`file_name`** (str): Document filename for display and download.
- **`size_mb`** (float): File size in megabytes.
- **`file_id`** (str or None): Drive file ID for browser viewing.

## Returns

**Type**: `ft.Column`


## Algorithm

- 1. **Build Info Display**:
    - a. BLUE DESCRIPTION icon (size 100)
    - b. Title: "Word Document" (size 20, bold)
    - c. Size text: f"Size: &#123;size_mb:.2f&#125; MB"
    - d. Notice: "Word preview is not available in-app" (italic, grey)
    - e. Advice: "Download to view full content" (size 12, grey)

  - 2. **Create Action Buttons**:
    - a. Download button → _download_file()
    - b. Open in Browser button (if file_id) → _open_in_browser()

  - 3. **Layout and Return**:
    - a. Vertical Column layout
    - b. Centered alignment
    - c. 10px spacing

## See Also

- `_create_pdf_preview()`: Similar structure
- `_download_file()`: Download handler
- `_open_in_browser()`: Browser opener

## Notes

- Supports both .doc and .docx
- No inline rendering (complex format)
- BLUE icon (standard Word color)
- Download for local viewing
- Browser opens Drive Docs viewer if available
