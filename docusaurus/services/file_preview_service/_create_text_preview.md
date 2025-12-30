---
id: "_create_text_preview"
sidebar_position: 10
title: "_create_text_preview"
---

# ⚙️ _create_text_preview

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`file_preview_service.py`](./file_preview_service.py) | **Line:** 1006
:::

Create scrollable text content preview with UTF-8 decoding.

Displays text file content in scrollable container. Handles UTF-8
decoding and shows error for binary files.

## Parameters

- **`file_data`** (bytes): Text file binary content. Expected to be UTF-8 encoded text. Non-UTF-8 files show decode error.
- **`size_mb`** (float): File size in megabytes for display.

## Returns

**Type**: `ft.Column`

                - Scrollable text container (grey background)
                - Character count and size info

## Algorithm

- 1. **Try Text Decoding**:
    - a. Enter try block for UTF-8 decode
    - b. Call file_data.decode('utf-8')
    - c. Store in text_content string

  - 2. **Build Text Viewer** (on success):
    - a. Create inner Column with text:
    - i. ft.Text with text_content
    - ii. Set selectable: True (allow copy)
    - iii. Set size: 13px (readable)
    - iv. Set scroll: "auto" (for long content)
    - b. Wrap in Container:
    - i. Set padding: 15px
    - ii. Set bgcolor: GREY_100 (light background)
    - iii. Set border_radius: 8px
    - iv. Set size: 650x450
    - v. Set border: 1px solid GREY_300
    - c. Create info text:
    - i. Format: f"Size: &#123;size_mb:.2f&#125; MB | &#123;len(text_content)&#125; characters"
    - ii. Size: 12px, color: GREY_600
    - d. Wrap in Column:
    - i. Container + info text
    - ii. horizontal_alignment: CENTER

  - 3. **Handle Decode Error**:
    - a. Catch UnicodeDecodeError
    - b. Create error Column:
    - i. Error icon (size 48, ORANGE)
    - ii. Text: "Cannot decode text file" (ORANGE)
    - iii. Text: "File may be binary or use unsupported encoding" (italic, size 12)
    - c. Set horizontal_alignment: CENTER

  - 4. **Return Widget**:
    - a. Return success Column or error Column

## Interactions

- **bytes.decode()**: UTF-8 text decoding
- **ft.Text**: Text content display

## Example

```python
# Internal usage from _render_preview
text_data = b'Hello World\\nLine 2'
widget = preview_service._create_text_preview(
    text_data,
    0.001
    )
# Shows "Hello World" in scrollable box

# Binary file error
binary_data = b'\\x00\\x01\\x02\\xFF'
widget = preview_service._create_text_preview(
    binary_data,
    0.001
    )
# Shows decode error message
```

## See Also

- `_render_preview()`: Calls this for text MIME types

## Notes

- Only supports UTF-8 encoding
- Binary files show decode error
- Text is selectable (copyable)
- Scrollable for long files
- Character count displayed
- Light grey background for readability
- Border for visual separation
- Error state user-friendly
