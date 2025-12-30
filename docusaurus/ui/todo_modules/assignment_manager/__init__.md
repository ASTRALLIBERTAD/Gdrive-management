---
id: "__init__"
sidebar_position: 3
title: "__init__"
---

# 🔧 __init__

![Completeness](https://img.shields.io/badge/Docs-20%25-red)

:::info Source
**File:** [`assignment_manager.py`](./assignment_manager.py) | **Line:** 50
:::

Initialize the AssignmentManager.

## Purpose

Sets up the manager with access to the parent view and initializes services.

## Parameters

- **`todo_view`** (TodoView): Parent view instance for accessing shared state.

## Interactions

- Stores `todo_view` reference.
- Initializes `FilePreviewService` (conditional import).
