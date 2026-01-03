"""Common Utility Functions.

This module provides shared helper functions for file I/O, URL handling, string
formatting, and creating common Flet UI elements like snackbars and dialogs.
"""

import flet as ft
import json
from pathlib import Path
from typing import Dict, Any


def load_json_file(filepath: str | Path, default: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Load and parse a JSON file with error handling and default fallback.

    Reads a JSON file from the filesystem, parses its contents, and returns
    the parsed data structure. Provides robust error handling for missing
    files, malformed JSON, and encoding issues, returning a default value
    when errors occur.

    Purpose:
        - Safely load JSON data from filesystem
        - Handle missing files gracefully with defaults
        - Parse JSON content into Python data structures
        - Provide error resilience for I/O and parsing failures

    Args:
        filepath (str | Path): Path to the JSON file to load. Can be either
            a string path or pathlib.Path object. Automatically converts
            strings to Path objects for consistent handling.
        default (any, optional): Value to return if file doesn't exist,
            cannot be read, or contains invalid JSON. If None, defaults
            to empty list []. Can be any Python object (list, dict, None, etc.).
            Defaults to None.

    Returns:
        any: Parsed JSON data as Python object (typically dict or list).
            Returns default value if file missing or parsing fails.
            Data type depends on JSON structure:
            - JSON object → dict
            - JSON array → list
            - JSON primitives → str, int, float, bool, None

    Algorithm:
        1. **Convert Path** (if needed):
           a. Check if filepath is string type
           b. If string, convert to Path object
           c. Ensures consistent path handling
        
        2. **Check File Existence**:
           a. Call filepath.exists() to verify file present
           b. If file doesn't exist, skip to step 5
        
        3. **Try File Reading and Parsing**:
           a. Enter try block for error handling
           b. Open file with UTF-8 encoding
           c. Use context manager (with) for automatic closing
           d. Call json.load(f) to parse JSON content
           e. Return parsed data immediately on success
        
        4. **Handle Errors**:
           a. Catch any exception (IOError, JSONDecodeError, etc.)
           b. Pass silently (no error logging)
           c. Fall through to default return
        
        5. **Return Default**:
           a. If default parameter is not None:
              i. Return provided default value
           b. If default is None:
              i. Return empty list []
           c. Provides safe fallback for missing/invalid files

    Interactions:
        - **pathlib.Path**: Path manipulation and existence checking
        - **json.load()**: JSON parsing from file object
        - **File I/O**: Opens and reads file with UTF-8 encoding

    Example:
        >>> # Load existing JSON file
        >>> data = load_json_file('config.json')
        >>> print(data)
        {'setting1': 'value1', 'setting2': 42}
        >>> 
        >>> # File doesn't exist, returns default (empty list)
        >>> data = load_json_file('missing.json')
        >>> print(data)
        []
        >>> 
        >>> # Custom default value
        >>> data = load_json_file('missing.json', default={'key': 'value'})
        >>> print(data)
        {'key': 'value'}
        >>> 
        >>> # Path object input
        >>> from pathlib import Path
        >>> data = load_json_file(Path('data.json'))
        >>> 
        >>> # Malformed JSON returns default
        >>> # File contains: {invalid json}
        >>> data = load_json_file('malformed.json', default=None)
        >>> print(data)
        None

    See Also:
        - :func:`save_json_file`: Save data to JSON file
        - :mod:`json`: Python JSON module
        - :class:`pathlib.Path`: Path manipulation

    Notes:
        - Automatically converts string paths to Path objects
        - Uses UTF-8 encoding for universal compatibility
        - Silent error handling (no exceptions raised)
        - Default value of None results in empty list return
        - Suitable for configuration files and data persistence
        - Thread-safe file reading with context manager
        - Does not create file if missing
    """
    if isinstance(filepath, str):
        filepath = Path(filepath)

    if filepath.exists():
        try:
            with filepath.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception:
            pass

    return default if default is not None else {}



def save_json_file(filepath, data):
    """Save Python data structure to a JSON file with formatting.

    Serializes Python data to JSON format and writes it to the specified
    file. Provides human-readable formatting with indentation, handles
    special types like datetime, and ensures proper Unicode encoding.

    Purpose:
        - Serialize Python objects to JSON format
        - Write JSON data to filesystem
        - Format JSON with indentation for readability
        - Handle special types (datetime, etc.) via str() conversion
        - Preserve Unicode characters (no ASCII escaping)

    Args:
        filepath (str | Path): Destination path for JSON file. Can be
            string path or pathlib.Path object. Automatically converts
            strings to Path for consistent handling. File created if
            doesn't exist; overwritten if exists.
        data (any): Python object to serialize. Must be JSON-serializable.
            Supported types: dict, list, str, int, float, bool, None.
            Non-standard types converted via str() (see default=str).

    Returns:
        bool: True if save successful, False if error occurred.
            Success: file written and closed properly.
            Failure: exception during write (logged to console).

    Algorithm:
        1. **Convert Path** (if needed):
           a. Check if filepath is string type
           b. If string, convert to Path object
           c. Ensures consistent path handling
        
        2. **Try File Writing**:
           a. Enter try block for error handling
           b. Open file in write mode with UTF-8 encoding
           c. Use context manager (with) for automatic closing
           d. Call json.dump() with configuration:
              i. indent=2 for readable formatting (2-space indent)
              ii. default=str to convert non-serializable types to strings
              iii. ensure_ascii=False to preserve Unicode characters
           e. Return True on successful write
        
        3. **Handle Errors**:
           a. Catch any Exception during write operation
           b. Print error message to console: f"Error saving: {e}"
           c. Return False to indicate failure

    Interactions:
        - **pathlib.Path**: Path manipulation
        - **json.dump()**: JSON serialization to file
        - **File I/O**: Opens and writes file with UTF-8 encoding

    Example:
        >>> # Save dictionary
        >>> data = {'name': 'LMS', 'version': '1.0', 'active': True}
        >>> success = save_json_file('config.json', data)
        >>> print(success)
        True
        >>> 
        >>> # File contents (formatted):
        >>> # {
        >>> #   "name": "LMS",
        >>> #   "version": "1.0",
        >>> #   "active": true
        >>> # }
        >>> 
        >>> # Save list
        >>> assignments = [
        ...     {'id': 1, 'title': 'Assignment 1'},
        ...     {'id': 2, 'title': 'Assignment 2'}
        ... ]
        >>> success = save_json_file('assignments.json', assignments)
        >>> 
        >>> # Save with datetime (converted to string)
        >>> from datetime import datetime
        >>> data = {'timestamp': datetime.now()}
        >>> success = save_json_file('log.json', data)
        >>> # timestamp field becomes string representation
        >>> 
        >>> # Handle write error (e.g., permission denied)
        >>> success = save_json_file('/root/protected.json', data)
        >>> print(success)
        False
        >>> # Console output: "Error saving: [Errno 13] Permission denied..."

    See Also:
        - :func:`load_json_file`: Load data from JSON file
        - :mod:`json`: Python JSON module
        - :class:`pathlib.Path`: Path manipulation

    Notes:
        - Creates file if doesn't exist
        - Overwrites existing file content
        - 2-space indentation for readability
        - default=str converts datetime, custom objects to strings
        - ensure_ascii=False preserves Unicode (emoji, non-Latin chars)
        - UTF-8 encoding for universal compatibility
        - Thread-safe writing with context manager
        - Prints errors to console (no exception raised)
        - Returns bool for caller error handling
    """
    if isinstance(filepath, str):
        filepath = Path(filepath)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving: {e}")
        return False


def format_file_size(size_bytes):
    """Format file size from bytes to human-readable string with units.

    Converts a byte count into a formatted string with appropriate unit
    suffix (B, KB, MB, GB, TB, PB). Automatically selects the most
    appropriate unit for readability (e.g., 1500000 → "1.4 MB").

    Purpose:
        - Convert raw byte counts to human-readable format
        - Automatically select appropriate size unit
        - Format with one decimal place precision
        - Handle edge cases (None, invalid input)

    Args:
        size_bytes (int | None): File size in bytes. Can be integer,
            numeric string convertible to int, or None. Negative values
            treated as errors. None indicates unknown size.

    Returns:
        str: Formatted size string with unit suffix. Examples:
            - "1.5 MB", "500 B", "2.3 GB"
            - "Unknown size" if input None or invalid

    Algorithm:
        1. **Check for None**:
           a. If size_bytes is None:
              i. Return "Unknown size" immediately
        
        2. **Try Conversion and Formatting**:
           a. Enter try block for error handling
           b. Convert size_bytes to integer: int(size_bytes)
           c. Store in size variable (float for division)
        
        3. **Iterate Through Units**:
           a. Define units list: ['B', 'KB', 'MB', 'GB', 'TB']
           b. For each unit in list:
              i. Check if size < 1024.0
              ii. If True:
                  - Format: f"{size:.1f} {unit}"
                  - Return formatted string immediately
              iii. If False:
                   - Divide size by 1024.0
                   - Continue to next unit
        
        4. **Handle Petabytes** (very large files):
           a. If loop completes without return:
              i. Size ≥ 1024 TB
              ii. Format as petabytes: f"{size:.1f} PB"
              iii. Return formatted string
        
        5. **Handle Errors**:
           a. Catch ValueError (invalid string) or TypeError (invalid type)
           b. Return "Unknown size"

    Interactions:
        - **int()**: Converts input to integer
        - **String formatting**: f-strings with .1f precision

    Example:
        >>> # Small file (bytes)
        >>> format_file_size(500)
        '500.0 B'
        >>> 
        >>> # Kilobytes
        >>> format_file_size(1536)
        '1.5 KB'
        >>> 
        >>> # Megabytes
        >>> format_file_size(1572864)
        '1.5 MB'
        >>> 
        >>> # Gigabytes
        >>> format_file_size(1610612736)
        '1.5 GB'
        >>> 
        >>> # None input
        >>> format_file_size(None)
        'Unknown size'
        >>> 
        >>> # Invalid input
        >>> format_file_size("invalid")
        'Unknown size'
        >>> 
        >>> # String numeric input
        >>> format_file_size("2048")
        '2.0 KB'

    See Also:
        - :class:`~services.drive_service.DriveService`: Uses this for file size display
        - :mod:`os.path`: File size retrieval

    Notes:
        - Uses 1024 divisor (binary units, not decimal)
        - One decimal place precision for all units
        - Handles input types: int, numeric string, None
        - Returns "Unknown size" for None or invalid input
        - Supports sizes up to petabytes (PB)
        - No negative size handling (treats as error)
        - Thread-safe (no state modification)
    """
    if size_bytes is None:
        return "Unknown size"
    try:
        size = int(size_bytes)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    except (ValueError, TypeError):
        return "Unknown size"


def extract_drive_id(url):
    """Extract Google Drive file or folder ID from various URL formats.

    Parses Google Drive URLs using regex patterns to extract the file or
    folder ID. Supports multiple Drive URL formats including file links,
    folder links, and query parameter formats. Returns raw input if it
    appears to already be an ID.

    Purpose:
        - Parse Drive URLs to extract file/folder IDs
        - Support multiple URL formats (folders, files, query params)
        - Handle raw ID input (pass-through)
        - Enable ID-based Drive API operations

    Args:
        url (str): Google Drive URL or ID to parse. Supported formats:
            - Folder: "https://drive.google.com/drive/folders/{id}"
            - File: "https://drive.google.com/file/d/{id}/view"
            - Query param: "...?id={id}"
            - Raw ID: alphanumeric string without slashes

    Returns:
        str | None: Extracted Drive ID if found, or None if no match.
            Returns input string if it appears to be raw ID (length > 20,
            no slashes). Drive IDs typically 33 characters alphanumeric.

    Algorithm:
        1. **Import Regex Module**:
           a. Import re for regex pattern matching
        
        2. **Define URL Patterns**:
           a. Create patterns list with regex strings:
              i. r"/folders/([a-zA-Z0-9_-]+)" - folder URLs
              ii. r"/file/d/([a-zA-Z0-9_-]+)" - file URLs
              iii. r"[?&]id=([a-zA-Z0-9_-]+)" - query parameter URLs
           b. Patterns capture ID in group 1
        
        3. **Try Pattern Matching**:
           a. For each pattern in patterns list:
              i. Call re.search(pattern, url)
              ii. If match found:
                  - Extract ID: match.group(1)
                  - Return ID immediately
        
        4. **Check for Raw ID**:
           a. If no pattern matched:
              i. Check if len(url) > 20 (IDs typically ~33 chars)
              ii. Check if "/" not in url (IDs have no slashes)
              iii. If both conditions true:
                   - Assume url is already an ID
                   - Return url as-is
        
        5. **Return None**:
           a. If no matches and not raw ID:
              i. Return None (invalid URL/ID)

    Interactions:
        - **re.search()**: Regex pattern matching
        - **re.Match.group()**: Extract captured group

    Example:
        >>> # Folder URL
        >>> url = "https://drive.google.com/drive/folders/1abc...xyz"
        >>> extract_drive_id(url)
        '1abc...xyz'
        >>> 
        >>> # File URL
        >>> url = "https://drive.google.com/file/d/1def...uvw/view"
        >>> extract_drive_id(url)
        '1def...uvw'
        >>> 
        >>> # Query parameter URL
        >>> url = "https://drive.google.com/open?id=1ghi...rst"
        >>> extract_drive_id(url)
        '1ghi...rst'
        >>> 
        >>> # Raw ID (pass-through)
        >>> id_str = "1jklmnopqrstuvwxyz123456789012"
        >>> extract_drive_id(id_str)
        '1jklmnopqrstuvwxyz123456789012'
        >>> 
        >>> # Invalid URL
        >>> extract_drive_id("https://example.com")
        None
        >>> 
        >>> # Short string (not ID)
        >>> extract_drive_id("short")
        None

    See Also:
        - :func:`open_drive_file`: Opens file using extracted ID
        - :func:`open_drive_folder`: Opens folder using extracted ID
        - :class:`~services.drive_service.DriveService`: Uses IDs for API calls

    Notes:
        - Supports folder, file, and query parameter URL formats
        - Drive IDs are alphanumeric with hyphens/underscores
        - Typical ID length is 33 characters
        - Raw ID detection uses length > 20 and no slashes
        - Returns None for invalid/unrecognized formats
        - Case-sensitive pattern matching (Drive IDs case-sensitive)
        - Thread-safe (no state modification)
    """
    import re
    patterns = [
        r"/folders/([a-zA-Z0-9_-]+)",
        r"/file/d/([a-zA-Z0-9_-]+)",
        r"[?&]id=([a-zA-Z0-9_-]+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    if len(url) > 20 and "/" not in url:
        return url
    
    return None


def open_url(url):
    """Open a URL in the system's default web browser.

    Launches the default web browser with the specified URL using the
    webbrowser module. Non-blocking operation that returns immediately
    after browser launch.

    Purpose:
        - Open URLs in default web browser
        - Support cross-platform browser launching
        - Provide non-blocking URL opening
        - Handle Drive links, websites, etc.

    Args:
        url (str): Complete URL to open including protocol (http://, https://).
            Examples: "https://drive.google.com/...", "https://example.com"

    Returns:
        None: Function executes as side effect (browser opens).

    Algorithm:
        1. **Import Module**:
           a. Import webbrowser from standard library
        
        2. **Open Browser**:
           a. Call webbrowser.open(url)
           b. System selects default browser
           c. Browser launches with URL
           d. Function returns immediately (non-blocking)

    Interactions:
        - **webbrowser.open()**: Launches system default browser

    Example:
        >>> # Open website
        >>> open_url("https://example.com")
        >>> # Browser opens to example.com
        >>> 
        >>> # Open Drive file
        >>> open_url("https://drive.google.com/file/d/abc123/view")
        >>> # Browser opens to Drive file viewer
        >>> 
        >>> # Open any URL
        >>> open_url("https://docs.google.com/document/d/xyz789")

    See Also:
        - :func:`open_drive_file`: Convenience wrapper for Drive files
        - :func:`open_drive_folder`: Convenience wrapper for Drive folders
        - :mod:`webbrowser`: Python webbrowser module

    Notes:
        - Uses system default browser (respects user preference)
        - Non-blocking operation (returns immediately)
        - No validation of URL format or accessibility
        - Browser process independent from Python application
        - May fail silently if no browser available (rare)
        - Cross-platform compatible (Windows, macOS, Linux)
    """
    import webbrowser
    webbrowser.open(url)


def open_drive_file(file_id):
    """Open a Google Drive file in the default web browser.

    Constructs a Drive file viewer URL from the file ID and opens it
    in the system's default browser. Convenience wrapper around open_url
    for Drive file links.

    Purpose:
        - Open Drive files in browser viewer
        - Construct proper Drive file URL from ID
        - Provide convenient API for Drive file opening

    Args:
        file_id (str): Google Drive file ID (typically 33-character
            alphanumeric string). Example: "1abc...xyz"

    Returns:
        None: Function executes as side effect (browser opens).

    Algorithm:
        1. **Construct URL**:
           a. Build URL string: f"https://drive.google.com/file/d/{file_id}/view"
           b. URL format: Drive file viewer endpoint
        
        2. **Open Browser**:
           a. Call open_url() with constructed URL
           b. Browser opens to Drive file viewer

    Interactions:
        - **open_url()**: Opens browser with constructed URL

    Example:
        >>> # Open Drive file
        >>> file_id = "1abc...xyz"
        >>> open_drive_file(file_id)
        >>> # Browser opens: https://drive.google.com/file/d/1abc...xyz/view
        >>> # User sees Drive file viewer

    See Also:
        - :func:`open_url`: Opens any URL in browser
        - :func:`open_drive_folder`: Opens Drive folder
        - :func:`extract_drive_id`: Extracts ID from Drive URL

    Notes:
        - Uses Drive's file viewer endpoint (/file/d/{id}/view)
        - User must have access permissions to view file
        - File opens in browser's Drive viewer (not downloaded)
        - Supports all Drive file types (docs, sheets, PDFs, images, etc.)
        - Non-blocking operation
    """
    open_url(f"https://drive.google.com/file/d/{file_id}/view")


def open_drive_folder(folder_id):
    """Open a Google Drive folder in the default web browser.

    Constructs a Drive folder URL from the folder ID and opens it in
    the system's default browser. Convenience wrapper around open_url
    for Drive folder links.

    Purpose:
        - Open Drive folders in browser
        - Construct proper Drive folder URL from ID
        - Provide convenient API for Drive folder opening

    Args:
        folder_id (str): Google Drive folder ID (typically 33-character
            alphanumeric string). Example: "1def...uvw"

    Returns:
        None: Function executes as side effect (browser opens).

    Algorithm:
        1. **Construct URL**:
           a. Build URL string: f"https://drive.google.com/drive/folders/{folder_id}"
           b. URL format: Drive folder listing endpoint
        
        2. **Open Browser**:
           a. Call open_url() with constructed URL
           b. Browser opens to Drive folder view

    Interactions:
        - **open_url()**: Opens browser with constructed URL

    Example:
        >>> # Open Drive folder
        >>> folder_id = "1def...uvw"
        >>> open_drive_folder(folder_id)
        >>> # Browser opens: https://drive.google.com/drive/folders/1def...uvw
        >>> # User sees folder contents in Drive

    See Also:
        - :func:`open_url`: Opens any URL in browser
        - :func:`open_drive_file`: Opens Drive file
        - :func:`extract_drive_id`: Extracts ID from Drive URL

    Notes:
        - Uses Drive's folder listing endpoint (/drive/folders/{id})
        - User must have access permissions to view folder
        - Shows folder contents in standard Drive interface
        - Non-blocking operation
    """
    open_url(f"https://drive.google.com/drive/folders/{folder_id}")


def create_icon_button(icon, tooltip, on_click, color=None):
    """Create a standard styled Flet IconButton with consistent configuration.

    Constructs an IconButton with the specified icon, tooltip, click handler,
    and optional color. Provides consistent button styling across the application.

    Purpose:
        - Create standardized icon buttons
        - Ensure consistent button styling
        - Provide accessibility via tooltips
        - Support custom icon colors

    Args:
        icon (str): Icon name from Flet's icon set (ft.Icons constants).
            Examples: ft.Icons.EDIT, ft.Icons.DELETE, ft.Icons.SAVE.
        tooltip (str): Tooltip text shown on hover. Should describe
            button action. Examples: "Edit assignment", "Delete file",
            "Save changes".
        on_click (Callable): Click event handler function. Signature:
            (e: ft.ControlEvent) -> None. Called when button clicked.
        color (ft.Colors, optional): Icon color. If None, uses default
            theme color. Examples: ft.Colors.RED, ft.Colors.BLUE.
            Defaults to None.

    Returns:
        ft.IconButton: Configured icon button control ready for use.

    Algorithm:
        1. **Create Button**:
           a. Instantiate ft.IconButton
           b. Set icon parameter to specified icon
           c. Set tooltip parameter to tooltip text
           d. Set on_click parameter to click handler
           e. Set icon_color parameter to specified color (or None)
        
        2. **Return Button**:
           a. Return configured IconButton instance

    Interactions:
        - **ft.IconButton**: Creates button component

    Example:
        >>> # Edit button
        >>> edit_btn = create_icon_button(
        ...     icon=ft.Icons.EDIT,
        ...     tooltip="Edit assignment",
        ...     on_click=lambda e: edit_assignment(),
        ...     color=ft.Colors.BLUE
        ... )
        >>> page.add(edit_btn)
        >>> 
        >>> # Delete button (red)
        >>> delete_btn = create_icon_button(
        ...     icon=ft.Icons.DELETE,
        ...     tooltip="Delete file",
        ...     on_click=lambda e: delete_file(),
        ...     color=ft.Colors.RED
        ... )
        >>> 
        >>> # Save button (default color)
        >>> save_btn = create_icon_button(
        ...     icon=ft.Icons.SAVE,
        ...     tooltip="Save changes",
        ...     on_click=handle_save
        ... )

    See Also:
        - :class:`ft.IconButton`: Flet icon button component
        - :class:`ft.Icons`: Flet icon constants

    Notes:
        - Returns configured button (not added to page)
        - Tooltip improves accessibility
        - Icon color optional (uses theme default if None)
        - Click handler receives ControlEvent parameter
        - Button can be styled further after creation
        - Icons from Material Design icon set
    """
    return ft.IconButton(
        icon=icon,
        tooltip=tooltip,
        on_click=on_click,
        icon_color=color
    )

def show_snackbar(page, message, color=ft.Colors.BLUE, duration=3):
    """Display a transient notification snackbar on a Flet page.

    Creates and displays a snackbar at the bottom of the page with the
    specified message and background color. Provides temporary user
    feedback that auto-dismisses after a few seconds.

    Purpose:
        - Display temporary notifications to users
        - Provide visual feedback for actions
        - Support color-coded message types (info/success/error/warning)
        - Auto-dismiss after brief period

    Args:
        page (ft.Page): Flet page instance where snackbar will be displayed.
            Must be active and rendered.
        message (str): Text message to display in snackbar. Should be
            concise and informative. Examples: "File saved", "Upload complete",
            "Error: Connection failed".
        color (ft.Colors, optional): Background color for snackbar.
            Used to indicate message type (blue=info, green=success,
            red=error, orange=warning). Defaults to ft.Colors.BLUE.

    Returns:
        None: Creates and displays snackbar as side effect.

    Algorithm:
        1. **Create Snackbar**:
           a. Instantiate ft.SnackBar
           b. Set content to ft.Text(message)
           c. Set bgcolor to specified color
        
        2. **Attach to Page**:
           a. Assign snackbar to page.snack_bar
           b. Replaces any existing snackbar
        
        3. **Show Snackbar**:
           a. Set page.snack_bar.open = True
           b. Makes snackbar visible
        
        4. **Update Page**:
           a. Call page.update()
           b. Renders snackbar at bottom of screen

    Interactions:
        - **ft.SnackBar**: Creates notification component
        - **ft.Text**: Message content
        - **ft.Page**: Displays and updates snackbar

    Example:
        >>> # Success message
        >>> show_snackbar(page, "Assignment saved!", ft.Colors.GREEN)
        >>> 
        >>> # Error message
        >>> show_snackbar(page, "Upload failed", ft.Colors.RED)
        >>> 
        >>> # Info message (default color)
        >>> show_snackbar(page, "Loading...")
        >>> 
        >>> # Warning message
        >>> show_snackbar(page, "Disk space low", ft.Colors.ORANGE)

    See Also:
        - :func:`create_dialog`: Alternative for modal dialogs
        - :class:`ft.SnackBar`: Flet snackbar component

    Notes:
        - Snackbar appears at bottom of screen
        - Auto-dismisses after a few seconds (Flet default)
        - Only one snackbar visible at a time (new replaces old)
        - Non-blocking (doesn't pause execution)
        - Color coding helps indicate message type
        - Message should be brief for readability
    """
    import threading
    
    toast = ft.Container(
        content=ft.Text(message, color=ft.Colors.WHITE),
        bgcolor=color,
        padding=10,
        border_radius=5,
        bottom=20,
        right=20,
        opacity=0.9,
        expand=True
    )
    
    page.overlay.append(toast)
    page.update()
    
    def remove_toast():
        import time
        time.sleep(duration)
        if toast in page.overlay:
            page.overlay.remove(toast)
            page.update()
    
    threading.Thread(target=remove_toast, daemon=True).start()