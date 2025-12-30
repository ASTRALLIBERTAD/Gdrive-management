---
id: "calculate_submission_timing"
sidebar_position: 4
title: "calculate_submission_timing"
---

# ⚙️ calculate_submission_timing

![Has Examples](https://img.shields.io/badge/Examples-✓-green) ![Has Algorithm](https://img.shields.io/badge/Algorithm-✓-blue) ![Completeness](https://img.shields.io/badge/Docs-60%25-orange)

:::info Source
**File:** [`submission_manager.py`](./submission_manager.py) | **Line:** 241
:::

Calculate whether a submission was early or late relative to deadline.

Parses submission and deadline timestamps, computes the time difference,
and returns a human-readable status message indicating whether the
submission was early or late. Supports both ISO 8601 and custom datetime
formats for backward compatibility.

## Parameters

- **`submitted_at_str`** (str): Timestamp of when assignment was submitted. Accepts ISO 8601 format (with 'T' separator) or custom format 'YYYY-MM-DD HH:MM'. Example: '2025-12-30T10:00:00' or '2025-12-30 10:00'.
- **`deadline_str`** (str): Deadline timestamp in ISO 8601 format. Example: '2025-12-31T23:59:00'.

## Returns

**Type**: `tuple`

                - status_code (str or None): 'early' if submitted before deadline,
                  'late' if submitted after deadline, None if data invalid.
                - message (str): Formatted human-readable timing message with emoji
                  and time breakdown. Examples: '✅ 1d 13h early', '⚠️ 2h 30m late',
                  'No timing data', 'Invalid timing data'.

## Algorithm

- 1. **Input Validation Phase**:
    - a. Check if submitted_at_str parameter is provided and not empty
    - b. Check if deadline_str parameter is provided and not empty
    - c. If either is missing, return tuple (None, "No timing data")
    - d. Proceed to parsing phase if both parameters valid

  - 2. **Submission Timestamp Parsing**:
    - a. Check if submitted_at_str contains 'T' character (ISO 8601 indicator)
    - b. If 'T' present:
    - - Parse using datetime.fromisoformat() for ISO 8601 format
    - - Example: '2025-12-30T10:00:00' → datetime object
    - c. If 'T' not present:
    - - Parse using strptime() with format '%Y-%m-%d %H:%M'
    - - Example: '2025-12-30 10:00' → datetime object
    - d. Store result in submitted_at variable

  - 3. **Deadline Timestamp Parsing**:
    - a. Parse deadline_str using datetime.fromisoformat() (always ISO 8601)
    - b. Example: '2025-12-31T23:59:00' → datetime object
    - c. Store result in deadline variable

  - 4. **Time Difference Calculation**:
    - a. Compute: time_diff = deadline - submitted_at
    - b. Result is timedelta object (can be positive or negative)
    - c. Extract total_seconds() to determine early vs late

  - 5. **Early Submission Processing** (time_diff > 0):
    - a. Check if time_diff.total_seconds() is positive
    - b. Extract components from time_diff:
    - - days = time_diff.days
    - - hours = time_diff.seconds // 3600
    - - minutes = (time_diff.seconds % 3600) // 60
    - c. Format message based on priority (days > hours > minutes):
    - - If days > 0: return ("early", "✅ &#123;days&#125;d &#123;hours&#125;h early")
    - - Elif hours > 0: return ("early", "✅ &#123;hours&#125;h &#123;minutes&#125;m early")
    - - Else: return ("early", "✅ &#123;minutes&#125;m early")

  - 6. **Late Submission Processing** (time_diff &lt;= 0):
    - a. Calculate absolute value: time_diff = abs(time_diff)
    - b. Extract components from absolute time_diff:
    - - days = time_diff.days
    - - hours = time_diff.seconds // 3600
    - - minutes = (time_diff.seconds % 3600) // 60
    - c. Format message based on priority (days > hours > minutes):
    - - If days > 0: return ("late", "⚠️ &#123;days&#125;d &#123;hours&#125;h late")
    - - Elif hours > 0: return ("late", "⚠️ &#123;hours&#125;h &#123;minutes&#125;m late")
    - - Else: return ("late", "⚠️ &#123;minutes&#125;m late")

  - 7. **Error Handling**:
    - a. Wrap entire process in try-except block
    - b. If any exception occurs (parsing error, calculation error):
    - - Catch exception silently
    - - Return tuple (None, "Invalid timing data")
    - c. This ensures function never crashes, always returns valid tuple

## Interactions

- **datetime.datetime**: Used for timestamp parsing and arithmetic
- **datetime.timedelta**: Represents time difference between dates

## Example

```python
# Early submission (1 day 13 hours early)
status, msg = calculate_submission_timing(
    '2025-12-30T10:00:00',
    '2025-12-31T23:59:00'
    )
print(f"{status}: {msg}")
# early: ✅ 1d 13h early

# Late submission (2 hours 30 minutes late)
status, msg = calculate_submission_timing(
    '2026-01-01T02:30:00',
    '2025-12-31T23:59:00'
    )
print(f"{status}: {msg}")
# late: ⚠️ 2h 30m late

# Custom format submission (30 minutes early)
status, msg = calculate_submission_timing(
    '2025-12-31 23:29',
    '2025-12-31T23:59:00'
    )
print(f"{status}: {msg}")
# early: ✅ 30m early

# Invalid data
status, msg = calculate_submission_timing(
    'invalid-date',
    '2025-12-31T23:59:00'
    )
print(f"{status}: {msg}")
# None: Invalid timing data
```

## See Also

- `submit_assignment_dialog()`: Uses timing for submission records
- `view_submissions_dialog()`: Displays timing in teacher interface
- `datetime`: Python datetime module documentation

## Notes

- Time breakdowns prioritize largest unit (days > hours > minutes)
- Displays only non-zero units in formatted message
- Handles both ISO 8601 and legacy datetime formats
- Returns None status for invalid or missing data
- Uses Unicode emoji for visual status indicators (✅/⚠️)
