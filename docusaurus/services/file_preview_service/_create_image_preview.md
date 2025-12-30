---
id: "_create_image_preview"
sidebar_position: 8
title: "_create_image_preview"
---

# ⚙️ _create_image_preview

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`file_preview_service.py`](./file_preview_service.py) | **Line:** 820
:::

Create inline image preview widget with base64 encoding.

Renders image directly in preview area using base64 data URI.
Suitable for PNG, JPEG, GIF, WebP, and other image formats.

## Parameters

- **`file_data`** (bytes): Raw image binary data. Any image format supported by browser (PNG, JPEG, GIF, WebP, BMP, SVG, etc.).
- **`size_mb`** (float): File size in megabytes for display. Calculated by caller from len(file_data) / (1024 * 1024).

## Returns

**Type**: `ft.Column`

                - ft.Image with base64-encoded src
                - ft.Text showing file size
                Both centered horizontally.

## Algorithm

- 1. **Encode Image Data**:
    - a. Call base64.b64encode(file_data)
    - b. Returns base64 bytes
    - c. Decode to string: .decode()
    - d. Store in base64_data

  - 2. **Create Image Widget**:
    - a. Instantiate ft.Image
    - b. Set src_base64: base64_data (data URI)
    - c. Set fit: CONTAIN (preserve aspect ratio)
    - d. Set width: 650px (fits overlay)
    - e. Set height: 450px (standard preview size)
    - f. Set border_radius: 8px (rounded corners)

  - 3. **Create Size Text**:
    - a. Format string: f"Size: &#123;size_mb:.2f&#125; MB"
    - b. Set size: 12px (small, info text)
    - c. Set color: GREY_600 (subtle)

  - 4. **Wrap in Column**:
    - a. Create ft.Column with [image, size_text]
    - b. Set horizontal_alignment: CENTER
    - c. Return Column widget

## Interactions

- **base64.b64encode()**: Encodes image data
- **ft.Image**: Displays image inline

## Example

```python
# Internal usage from _render_preview
image_data = b'\\x89PNG...'  # PNG file bytes
widget = preview_service._create_image_preview(
    image_data,
    size_mb=1.5
    )
# Returns Column with image and "Size: 1.50 MB"
```

## See Also

- `_render_preview()`: Calls this for image MIME types
- `base64`: Image encoding

## Notes

- Base64 encoding increases size by ~33%
- Suitable for images up to ~5-10MB
- Very large images may impact performance
- Image fit: CONTAIN preserves aspect ratio
- Width/height constrain maximum display size
- Supports all browser-compatible image formats
- No pagination for multi-page formats (e.g., TIFF)
