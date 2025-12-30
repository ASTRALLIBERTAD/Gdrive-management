---
id: "show_notifications_dialog"
sidebar_position: 19
title: "show_notifications_dialog"
---

# ⚙️ show_notifications_dialog

![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-0%25-red)

:::info Source
**File:** [`assignment_manager.py`](./assignment_manager.py) | **Line:** 1103
:::

Show a dialog listing recent notifications for the current student.

## Purpose

Displays a scrollable list of alerts/messages and allows marking them as read.

## Algorithm

- 1. Fetch notifications for current email.
  - 2. Render list:
    - a. Highlight unread items.
    - b. Click to mark read.
  - 3. Provide "Mark All Read" button.
  - 4. Show in Overlay.

## Interactions

- Calls `notification_service.get_notifications_for_student`.
- Calls `notification_service.mark_as_read`.
