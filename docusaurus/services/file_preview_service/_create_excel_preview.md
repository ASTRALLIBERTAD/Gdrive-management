---
id: "_create_excel_preview"
sidebar_position: 12
title: "_create_excel_preview"
---

# ⚙️ _create_excel_preview

![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`file_preview_service.py`](./file_preview_service.py) | **Line:** 1186
:::

Create Microsoft Excel placeholder with download and browser options.

Shows Excel icon and metadata. No inline spreadsheet viewer.

## Parameters

- **`file_data`** (bytes): Excel file binary content (.xls or .xlsx).
- **`file_name`** (str): Spreadsheet filename for display and download.
- **`size_mb`** (float): File size in megabytes.
- **`file_id`** (str or None): Drive file ID for browser viewing.

## Returns

**Type**: `ft.Column`


## Algorithm

- Similar to _create_word_preview but with:
  - - GREEN TABLE_CHART icon
  - - Title: "Spreadsheet Document"
  - - Download button: "Download Spreadsheet"
  - - GREEN Open button color

## See Also

- `_create_word_preview()`: Similar structure

## Notes

- Supports both .xls and .xlsx
- GREEN icon (standard Excel color)
- No inline grid viewer
