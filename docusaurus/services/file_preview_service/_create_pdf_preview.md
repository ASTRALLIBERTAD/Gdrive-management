---
id: "_create_pdf_preview"
sidebar_position: 9
title: "_create_pdf_preview"
---

# ⚙️ _create_pdf_preview

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`file_preview_service.py`](./file_preview_service.py) | **Line:** 902
:::

Create PDF placeholder with download and browser viewing options.

Shows PDF icon and metadata with action buttons. No inline PDF viewer
(browser/external viewer required for actual content).

## Parameters

- **`file_data`** (bytes): PDF binary content. Used for download functionality. Not rendered inline.
- **`file_name`** (str): PDF filename for display and download.
- **`size_mb`** (float): File size in megabytes for display.
- **`file_id`** (str or None): Drive file ID for browser viewing. If None, only download button shown.

## Returns

**Type**: `ft.Column`


## Algorithm

- 1. **Build Info Display**:
    - a. Create RED PDF icon (PICTURE_AS_PDF, size 100)
    - b. Create title: "PDF Document" (size 20, bold)
    - c. Create size text: f"Size: &#123;size_mb:.2f&#125; MB" (size 14)
    - d. Create notice: "PDF preview is not available in-app" (italic, grey)

  - 2. **Create Action Buttons**:
    - a. Create Download button:
    - i. Text: "Download PDF"
    - ii. Icon: DOWNLOAD
    - iii. on_click: lambda e: _download_file(file_data, file_name)
    - b. If file_id exists:
    - i. Create Open button:
    - - Text: "Open in Browser"
    - - Icon: OPEN_IN_NEW
    - - on_click: lambda e: _open_in_browser(file_id)
    - - bgcolor: BLUE
    - c. If file_id is None:
    - i. Use empty Container (no browser button)

  - 3. **Layout Actions Row**:
    - a. Create ft.Row with action buttons
    - b. Set spacing: 10px between buttons

  - 4. **Assemble Column**:
    - a. Create ft.Column with all elements
    - b. Set horizontal_alignment: CENTER
    - c. Set spacing: 10px between elements
    - d. Return Column widget

## Interactions

- **_download_file()**: Saves PDF to Downloads
- **_open_in_browser()**: Opens in Drive web viewer

## Example

```python
# Internal usage from _render_preview
pdf_data = b'%PDF-1.4...'
widget = preview_service._create_pdf_preview(
    pdf_data,
    'document.pdf',
    2.5,
    'drive_id'
    )
# Shows PDF placeholder with both buttons
```

## See Also

- `_render_preview()`: Calls this for PDF MIME type
- `_download_file()`: Download handler
- `_open_in_browser()`: Browser opener

## Notes

- No inline PDF viewer (browser plugin required)
- Download saves to Downloads folder
- Browser view requires Drive file_id
- Local PDFs only show download option
- Icon color RED (standard PDF indicator)
- Buttons horizontal layout with spacing
