---
id: "open_drive_file"
sidebar_position: 7
title: "open_drive_file"
---

# ⚙️ open_drive_file

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`common.py`](./common.py) | **Line:** 545
:::

Open a Google Drive file in the default web browser.

Constructs a Drive file viewer URL from the file ID and opens it
in the system's default browser. Convenience wrapper around open_url
for Drive file links.

## Purpose

- Open Drive files in browser viewer
        - Construct proper Drive file URL from ID
        - Provide convenient API for Drive file opening

## Parameters

- **`file_id`** (str): Google Drive file ID (typically 33-character alphanumeric string). Example: "1abc...xyz"

## Returns

**Type**: `None`


## Algorithm

- 1. **Construct URL**:
- a. Build URL string: f"https://drive.google.com/file/d/&#123;file_id&#125;/view"
- b. URL format: Drive file viewer endpoint

- 2. **Open Browser**:
- a. Call open_url() with constructed URL
- b. Browser opens to Drive file viewer

## Interactions

- **open_url()**: Opens browser with constructed URL

## Example

```python
# Open Drive file
file_id = "1abc...xyz"
open_drive_file(file_id)
# Browser opens: https://drive.google.com/file/d/1abc...xyz/view
# User sees Drive file viewer
```

## See Also

- `open_url()`: Opens any URL in browser
- `open_drive_folder()`: Opens Drive folder
- `extract_drive_id()`: Extracts ID from Drive URL

## Notes

- Uses Drive's file viewer endpoint (/file/d/&#123;id&#125;/view)
- User must have access permissions to view file
- File opens in browser's Drive viewer (not downloaded)
- Supports all Drive file types (docs, sheets, PDFs, images, etc.)
- Non-blocking operation
