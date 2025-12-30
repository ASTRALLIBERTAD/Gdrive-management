---
id: "_build_ui"
sidebar_position: 4
title: "_build_ui"
---

# ⚙️ _build_ui

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-40%25-red)

:::info Source
**File:** [`login.py`](./login.py) | **Line:** 245
:::

Construct and arrange all login interface UI components.

Builds the complete user interface by creating and configuring all UI
elements including header, status text, login button, and security notice.
Arranges components in a centered, vertically-stacked layout with
consistent spacing and styling.

## Returns

**Type**: `None`

                Also stores references to status_text and login_button in
                instance attributes for dynamic updates.

## Algorithm

- 1. **Detect Platform**:
    - a. Call _get_platform_name() to get human-readable platform name
    - b. Store result in platform_name variable
    - c. Used for display text (e.g., "Platform: Windows")

  - 2. **Add Header Components**:
    - a. Add 50px vertical spacing Container at top
    - b. Add cloud icon (ft.Icons.CLOUD_CIRCLE):
    - - Size: 100px
    - - Color: BLUE_600 (brand blue)
    - c. Add title text "Learning Management System":
    - - Size: 32px (large, prominent)
    - - Weight: BOLD
    - - Alignment: CENTER
    - d. Add subtitle text "Access your learning materials anywhere":
    - - Size: 16px (medium)
    - - Color: GREY_700 (subtle)
    - - Alignment: CENTER
    - e. Add 10px vertical spacing Container
    - f. Add platform indicator text:
    - - Format: "Platform: &#123;platform_name&#125;"
    - - Size: 12px (small)
    - - Color: GREY_600 (very subtle)
    - - Alignment: CENTER
    - g. Add 20px vertical spacing Container

  - 3. **Create Status Text**:
    - a. Instantiate ft.Text with initial message
    - b. Set text: "Please log in to continue"
    - c. Set color: GREY_700 (neutral, informative)
    - d. Set text_align: CENTER
    - e. Store reference in self.status_text
    - f. Append to self.controls

  - 4. **Create Login Button**:
    - a. Instantiate ft.ElevatedButton with configuration:
    - - text: "Login with Google"
    - - icon: ft.Icons.LOGIN (sign-in icon)
    - - on_click: self.handle_login (delegated to subclass)
    - b. Define button style:
    - - bgcolor: BLUE_600 (Google blue theme)
    - - color: WHITE (text color)
    - - padding: symmetric(horizontal=30, vertical=15)
    - c. Set height to 50px (prominent, touch-friendly)
    - d. Store reference in self.login_button
    - e. Add 10px spacing Container before button
    - f. Append button to self.controls

  - 5. **Add Security Notice**:
    - a. Add 20px vertical spacing Container
    - b. Add security text:
    - - Content: "Secure authentication via Google OAuth 2.0"
    - - Size: 12px (small, informational)
    - - Color: GREY_500 (very subtle)
    - - Alignment: CENTER
    - - Italic: True (distinguishes from other text)
    - c. Append to self.controls

## Interactions

- **_get_platform_name()**: Retrieves platform name for display
- **ft.Text, ft.Icon, ft.Container, ft.ElevatedButton**:
- Flet UI components for interface construction
- **handle_login()**: Abstract method called on button click

## Example

```python
# After initialization
login = ConcreteLoginSubclass(page, auth, callback)
# _build_ui already called in __init__
print(len(login.controls))
# 14  # Header + status + button + security notice + spacing
print(login.status_text.value)
# Please log in to continue
print(login.login_button.text)
# Login with Google
print(login.login_button.disabled)
# False
```

## See Also

- `_get_platform_name()`: Platform detection helper
- `handle_login()`: Login button click handler (abstract)
- `__init__()`: Calls this method during initialization

## Notes

- Components added to self.controls in display order (top to bottom)
- Status text and login button stored for later updates
- Button enabled initially, disabled during authentication
- Spacing containers provide visual separation between sections
- All text elements centered for mobile-friendly layout
- Button height (50px) and padding optimized for touch input
- Security notice builds user trust and transparency
