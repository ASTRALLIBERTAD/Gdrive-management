"""Todo View Module.

This module acts as the main container and orchestrator for the Learning Management
System (LMS) features. It integrates various managers to handle assignments,
student data, storage, and submissions, providing a unified UI for teachers
and students.

Classes:
    TodoView: The primary UI view for the LMS dashboard.

See Also:
    :class:`~src.ui.dashboard.Dashboard`: The parent dashboard container.
    :mod:`src.ui.todo_modules`: Package containing specialized logic managers.
"""

import flet as ft
import json
import os
from pathlib import Path

SAVED_LINKS_FILE = "saved_links.json"
LMS_CONFIG_FILE = "lms_config.json"


class TodoView:
    """Main orchestrator and UI controller for the Learning Management System.

    TodoView serves as the central hub that coordinates all LMS functionality,
    integrating assignment management, student administration, file storage,
    submission tracking, and UI presentation. It manages the view state (teacher
    vs student mode), handles persistent data loading/saving, and provides the
    primary interface for both educators and learners.
    
    This class follows the Facade pattern, presenting a unified interface to
    multiple complex subsystems (assignments, students, storage, submissions).
    It maintains the application state, manages UI components, and delegates
    specialized operations to manager classes while handling cross-cutting
    concerns like overlays, snackbars, and navigation.

    Purpose:
        - Orchestrate interactions between UI and manager subsystems
        - Maintain application state (mode, current user, selections)
        - Provide unified interface for LMS functionality
        - Handle persistent data loading and saving
        - Manage UI layout and component lifecycle
        - Support role-based views (teacher/student modes)
        - Facilitate file attachments and Drive integration
        - Display assignments, students, and submissions

    Attributes:
        page (ft.Page): Flet page instance for UI rendering and updates.
            Provides access to overlay system, update mechanism, and
            platform detection.
        on_back (Callable or None): Optional callback function invoked when
            user clicks back button to return to dashboard. Signature: () -> None.
        drive_service (DriveService or None): Google Drive service wrapper
            providing file/folder operations, metadata queries, and permissions
            management. May be None if Drive integration unavailable.
        data_dir (Path): Local directory path for storing LMS data files
            (assignments.json, students.json, submissions.json). Created
            automatically if doesn't exist.
        data_manager (DataManager): Manager handling JSON serialization,
            deserialization, and persistence of assignments, students, and
            submissions data.
        storage_manager (StorageManager): Manager coordinating Drive folder
            operations, link handling, and file upload/download functionality.
        assignment_manager (AssignmentManager): Manager implementing assignment
            CRUD operations, rendering logic, and deadline calculations.
        student_manager (StudentManager): Manager handling student registration,
            enrollment, type classification (bridging/regular), and dropdown
            population.
        submission_manager (SubmissionManager): Manager coordinating submission
            flow, grading interface, file preview, and timing calculations.
        assignments (list): In-memory list of assignment dictionaries. Each
            assignment contains: id, title, description, subject, deadline,
            drive_folder_id, file_path, file_name, max_score, target_for, etc.
        students (list): In-memory list of student dictionaries. Each student
            contains: email, name, student_type ('bridging' or 'regular').
        submissions (list): In-memory list of submission dictionaries. Each
            submission contains: id, assignment_id, student_email, submitted_at,
            grade, feedback, file_id, file_name, file_link, etc.
        saved_links (list): Legacy list of saved Drive folder shortcuts.
            Each link: {id, name, url}. Loaded from saved_links.json.
        notification_service (NotificationService or None): Optional service
            for managing assignment notifications and reminders. None if
            import fails.
        current_mode (str): Active view mode. Values: 'teacher' (default)
            or 'student'. Controls UI visibility and available operations.
        current_student_email (str or None): Email of currently selected
            student in student view mode. None if no student selected.
        assignment_title (ft.TextField): Input field for assignment title.
        assignment_description (ft.TextField): Multiline input for assignment
            instructions/description.
        subject_dropdown (ft.Dropdown): Subject selection dropdown with
            predefined options (Math, Science, English, etc.).
        max_score_field (ft.TextField): Numeric input for maximum assignment score.
        target_dropdown (ft.Dropdown): Target audience selector (All/Bridging/Regular).
        selected_drive_folder_id (str or None): Currently selected Drive folder
            ID for assignment attachment.
        drive_folder_label (ft.Text): Display text showing selected folder name.
        attachment_text (ft.Text): Display text showing attached file name.
        selected_attachment (dict): Dictionary with 'path' and 'name' keys for
            local file attachment.
        selected_date_value (datetime.date or None): Selected deadline date.
        selected_time_value (datetime.time or None): Selected deadline time.
        selected_deadline_display (ft.Text): Display text showing combined
            date and time deadline.
        date_picker (ft.DatePicker): Date picker dialog control.
        time_picker (ft.TimePicker): Time picker dialog control.
        assignment_column (ft.Column): Scrollable container displaying assignment
            cards. Updated dynamically based on mode and filters.
        filter_dropdown (ft.Dropdown): Filter selector for assignments
            (All/Active/Completed/Overdue).
        mode_switch (ft.Switch): Toggle control for teacher/student mode.
        mode_label (ft.Text): Display label showing current mode with emoji.
        settings_btn (ft.ElevatedButton): Button opening storage settings dialog.
        student_dropdown (ft.Dropdown): Student selector in student view mode.
        student_selector_row (ft.Row): Container for student selection controls,
            visible only in student mode.
        form_container (ft.Container or None): Container wrapping assignment
            creation form, visible only in teacher mode.
        manage_students_btn (ft.ElevatedButton or None): Button opening student
            management dialog, visible only in teacher mode.

    Interactions:
        - **DataManager**: Loads/saves assignments, students, submissions
        - **StorageManager**: Handles Drive folder selection and file uploads
        - **AssignmentManager**: Renders assignments and handles CRUD operations
        - **StudentManager**: Manages student data and dropdown population
        - **SubmissionManager**: Coordinates submission and grading workflows
        - **DriveService**: Provides Drive API operations (if available)
        - **NotificationService**: Manages notifications (if available)
        - **ft.Page**: Updates UI and manages overlays/dialogs

    Algorithm (High-Level Workflow):
        **Phase 1: Initialization**
            1. Store page, callback, and Drive service references
            2. Create data directory (lms_data) if not exists
            3. Import and instantiate manager classes:
               - DataManager for persistence
               - StorageManager for Drive operations
               - AssignmentManager for assignment logic
               - StudentManager for student management
               - SubmissionManager for submission handling
            4. Load persistent data:
               - assignments from data_manager
               - students from data_manager
               - submissions from data_manager
               - saved_links from JSON file
            5. Optionally initialize NotificationService
            6. Set default state: teacher mode, no student selected
            7. Initialize all UI components via _init_ui_components()
        
        **Phase 2: UI Component Initialization** (_init_ui_components)
            1. Create input fields (title, description, max_score)
            2. Create dropdowns (subject, target, filter, student)
            3. Create pickers (date, time, file)
            4. Create display texts (folder, attachment, deadline)
            5. Create layout containers (assignment_column, form_container)
            6. Create controls (mode_switch, mode_label, buttons)
            7. Store all components as instance attributes
        
        **Phase 3: View Rendering** (get_view)
            1. Display current assignments via display_assignments()
            2. Build assignment creation form (teacher mode only)
            3. Create header with back button, icon, title
            4. Build mode switcher row with settings button
            5. Add student selector row (student mode only)
            6. Add form container (teacher mode only)
            7. Build assignment list section with filter
            8. Assemble complete layout in Column
            9. Return root Column control
        
        **Phase 4: Mode Switching** (switch_mode)
            1. Toggle current_mode based on switch value
            2. Update mode_label text and emoji
            3. Show/hide student selector row
            4. Show/hide form container
            5. Show/hide manage students button
            6. Refresh assignment display
            7. Update page
        
        **Phase 5: Assignment Display** (display_assignments)
            1. Clear assignment_column controls
            2. Check current_mode
            3. If teacher: delegate to assignment_manager.display_teacher_view()
            4. If student: delegate to assignment_manager.display_student_view()
            5. Update page to render changes
        
        **Phase 6: Data Interaction**
            1. User creates/edits/deletes assignment
            2. Manager updates in-memory list
            3. DataManager saves to JSON file
            4. UI refreshes to show changes
        
        **Phase 7: File/Folder Selection**
            1. User clicks file/folder picker button
            2. Picker dialog opens
            3. User selects file/folder
            4. Callback updates selected_* attributes
            5. Display text updates to show selection
            6. Page updates to render changes

    Example:
        >>> # Initialize TodoView with page and services
        >>> todo_view = TodoView(
        ...     page=page,
        ...     on_back=lambda: page.go('/dashboard'),
        ...     drive_service=drive
        ... )
        >>> 
        >>> # Get view layout and add to page
        >>> layout = todo_view.get_view()
        >>> page.add(layout)
        >>> page.update()
        >>> 
        >>> # User in teacher mode sees:
        >>> # - Assignment creation form
        >>> # - List of all assignments
        >>> # - Manage students button
        >>> 
        >>> # User switches to student mode
        >>> todo_view.switch_mode(switch_event)
        >>> # User now sees:
        >>> # - Student selector dropdown
        >>> # - Assignments assigned to selected student
        >>> # - Submit buttons on assignments
        >>> 
        >>> # Display success message
        >>> todo_view.show_snackbar("Assignment created!", ft.Colors.GREEN)

    See Also:
        - :class:`~ui.todo_modules.data_manager.DataManager`: Data persistence
        - :class:`~ui.todo_modules.assignment_manager.AssignmentManager`: Assignment logic
        - :class:`~ui.todo_modules.student_manager.StudentManager`: Student management
        - :class:`~ui.todo_modules.submission_manager.SubmissionManager`: Submission handling
        - :class:`~ui.todo_modules.storage_manager.StorageManager`: Drive operations
        - :class:`~ui.dashboard.Dashboard`: Parent dashboard container
        - :class:`~services.drive_service.DriveService`: Drive API wrapper

    Notes:
        - Data directory created automatically on initialization
        - Manager classes receive self reference for accessing shared state
        - In-memory data lists modified by managers, saved by DataManager
        - UI components stored as attributes for dynamic updates
        - Mode switch controls visibility of role-specific components
        - Drive service optional - features gracefully degrade if None
        - Notification service optional - loaded conditionally
        - Overlay system supports modal dialogs with custom content
        - Snackbar provides transient notifications
        - Filter dropdown dynamically updates assignment display
        - Student dropdown includes registration option
        - File attachments support local files and Drive folders
        - Deadline selection uses two-step process (date then time)

    Design Patterns:
        - **Facade Pattern**: Provides unified interface to complex subsystems
        - **Mediator Pattern**: Coordinates interactions between managers
        - **Observer Pattern**: UI updates triggered by state changes

    References:
        - Flet Framework: https://flet.dev/docs/
        - Facade Pattern: https://refactoring.guru/design-patterns/facade
        - Google Drive API: https://developers.google.com/drive/api/v3/reference
    """
    
    def __init__(self, page: ft.Page, on_back=None, drive_service=None):
        """Initialize TodoView with page, navigation callback, and Drive service.

        Constructs the LMS view by setting up data persistence, instantiating
        manager subsystems, loading existing data, and initializing all UI
        components. Prepares the complete application state for rendering.

        Args:
            page (ft.Page): Flet page instance for UI rendering, updates, and
                overlay management. Must be initialized and active.
            on_back (Callable, optional): Callback function invoked when user
                clicks back button. Typically navigates to dashboard. Signature:
                () -> None. Defaults to None (back button hidden).
            drive_service (DriveService, optional): Google Drive service wrapper
                providing file/folder operations. If None, Drive features are
                disabled or degraded. Defaults to None.

        Algorithm:
            1. **Store Core References**:
               a. Assign page to self.page
               b. Assign on_back to self.on_back
               c. Assign drive_service to self.drive_service
            
            2. **Setup Data Directory**:
               a. Create Path object: Path("lms_data")
               b. Store in self.data_dir
               c. Call mkdir(exist_ok=True) to create if needed
               d. Directory contains JSON files for persistence
            
            3. **Import Manager Classes**:
               a. Import DataManager from ui.todo_modules.data_manager
               b. Import StorageManager from ui.todo_modules.storage_manager
               c. Import AssignmentManager from ui.todo_modules.assignment_manager
               d. Import StudentManager from ui.todo_modules.student_manager
               e. Import SubmissionManager from ui.todo_modules.submission_manager
            
            4. **Instantiate Managers**:
               a. Create DataManager(data_dir, drive_service)
               b. Create StorageManager(self, drive_service)
               c. Create AssignmentManager(self)
               d. Create StudentManager(self)
               e. Create SubmissionManager(self)
               f. Each manager stores reference to TodoView (self)
            
            5. **Load Persistent Data**:
               a. Call data_manager.load_assignments() -> list
               b. Store in self.assignments
               c. Call data_manager.load_students() -> list
               d. Store in self.students
               e. Call data_manager.load_submissions() -> list
               f. Store in self.submissions
               g. Call self.load_saved_links() -> list
               h. Store in self.saved_links
            
            6. **Initialize Notification Service** (optional):
               a. Try to import NotificationService
               b. If successful:
                  i. Instantiate NotificationService(data_dir)
                  ii. Store in self.notification_service
               c. If ImportError:
                  i. Set self.notification_service = None
                  ii. Feature gracefully disabled
            
            7. **Set Initial State**:
               a. Set self.current_mode = "teacher"
               b. Set self.current_student_email = None
               c. Default view is teacher mode with no student selected
            
            8. **Initialize UI Components**:
               a. Call self._init_ui_components()
               b. Creates all input fields, dropdowns, pickers, etc.
               c. Stores components as instance attributes
               d. Components ready for get_view() to assemble

        Interactions:
            - **Path.mkdir()**: Creates data directory
            - **DataManager**: Loads assignments, students, submissions
            - **load_saved_links()**: Loads legacy link shortcuts
            - **_init_ui_components()**: Creates UI controls
            - **Manager classes**: Instantiated with references

        Example:
            >>> # Create with full configuration
            >>> todo = TodoView(
            ...     page=page,
            ...     on_back=lambda: page.go('/dashboard'),
            ...     drive_service=drive
            ... )
            >>> print(len(todo.assignments))
            5
            >>> print(todo.current_mode)
            teacher
            >>> 
            >>> # Create with minimal configuration
            >>> todo_minimal = TodoView(page=page)
            >>> print(todo_minimal.on_back)
            None
            >>> print(todo_minimal.drive_service)
            None

        See Also:
            - :meth:`_init_ui_components`: Initializes UI controls
            - :meth:`load_saved_links`: Loads legacy link data
            - :meth:`get_view`: Assembles UI layout
            - :class:`~ui.todo_modules.data_manager.DataManager`: Data persistence

        Notes:
            - Data directory created automatically if doesn't exist
            - Manager instantiation order important (DataManager first)
            - In-memory data lists updated by managers throughout lifecycle
            - Notification service optional (None if import fails)
            - Drive service optional (features degrade gracefully if None)
            - Initial mode is teacher (assignments writable)
            - UI components not attached to page until get_view() called
        """
        self.page = page
        self.on_back = on_back
        self.drive_service = drive_service
        
        self.data_dir = Path("lms_data")
        self.data_dir.mkdir(exist_ok=True)
        
        from ui.todo_modules.data_manager import DataManager
        from ui.todo_modules.storage_manager import StorageManager
        from ui.todo_modules.assignment_manager import AssignmentManager
        from ui.todo_modules.student_manager import StudentManager
        from ui.todo_modules.submission_manager import SubmissionManager
        
        self.data_manager = DataManager(self.data_dir, drive_service)
        self.storage_manager = StorageManager(self, drive_service)
        self.assignment_manager = AssignmentManager(self)
        self.student_manager = StudentManager(self)
        self.submission_manager = SubmissionManager(self)
        
        self.assignments = self.data_manager.load_assignments()
        self.students = self.data_manager.load_students()
        self.submissions = self.data_manager.load_submissions()
        self.saved_links = self.load_saved_links()
        
        try:
            from services.notification_service import NotificationService
            self.notification_service = NotificationService(self.data_dir)
        except ImportError:
            self.notification_service = None
        
        self.current_mode = "teacher"
        self.current_student_email = None
        
        self._init_ui_components()
        
    def _init_ui_components(self):
        """Initialize all persistent UI controls and layout containers.

        Creates and configures every UI component used by TodoView including
        input fields, dropdowns, pickers, display texts, buttons, and layout
        containers. Stores all components as instance attributes for later
        access and modification. Does not attach components to page; assembly
        happens in get_view().

        Returns:
            None: Creates and stores UI components as instance attributes.

        Algorithm:
            1. **Create Input Fields**:
               a. Create assignment_title TextField (hint: "Assignment Title")
               b. Create assignment_description TextField:
                  - Multiline: True
                  - Min lines: 3, max lines: 5
                  - Hint: "Description/Instructions"
               c. Create max_score_field TextField:
                  - Width: 150px
                  - Keyboard type: NUMBER
                  - Input filter: NumbersOnlyInputFilter
            
            2. **Create Dropdown Selectors**:
               a. Create subject_dropdown with options:
                  - Mathematics, Science, English, History
                  - Computer Science, Arts, Physical Education, Other
                  - Width: 200px
               b. Create target_dropdown with options:
                  - "all" -> "All Students"
                  - "bridging" -> "Bridging Only"
                  - "regular" -> "Regular Only"
                  - Default value: "all", width: 200px
               c. Create filter_dropdown with options:
                  - All, Active, Completed, Overdue
                  - Default: "All", width: 150px
                  - on_change: lambda e: display_assignments()
               d. Create student_dropdown:
                  - Width: 250px
                  - on_change: on_student_selected
                  - Populated by student_manager
            
            3. **Initialize Drive Folder Selection**:
               a. Set selected_drive_folder_id = None
               b. Create drive_folder_label Text:
                  - Value: "No folder selected"
                  - Size: 12px, italic: True
            
            4. **Initialize File Attachment**:
               a. Create attachment_text Text:
                  - Value: "No file attached"
                  - Size: 12px, italic: True
               b. Create selected_attachment dict:
                  - Keys: "path", "name"
                  - Initial values: None
            
            5. **Initialize Deadline Selection**:
               a. Set selected_date_value = None
               b. Set selected_time_value = None
               c. Create selected_deadline_display Text:
                  - Value: "No deadline selected"
                  - Size: 12px, italic: True
               d. Create date_picker DatePicker:
                  - on_change: on_date_selected
               e. Create time_picker TimePicker:
                  - on_change: on_time_selected
            
            6. **Create Layout Containers**:
               a. Create assignment_column Column:
                  - Scroll: "auto", expand: True
                  - Spacing: 10px
                  - Will hold assignment cards
            
            7. **Create Mode Controls**:
               a. Create mode_switch Switch:
                  - Value: False (teacher mode)
                  - on_change: switch_mode
               b. Create mode_label Text:
                  - Value: "👨‍🏫 Teacher View"
                  - Size: 16px, weight: BOLD
            
            8. **Create Action Buttons**:
               a. Create settings_btn ElevatedButton:
                  - Text: "Storage"
                  - Icon: SETTINGS
                  - on_click: storage_manager.show_storage_settings
            
            9. **Create Student Selector Row**:
               a. Create student_selector_row Row:
                  - Contains: Text("Viewing as:"), student_dropdown
                  - Visible: False (only in student mode)
               b. Call student_manager.update_student_dropdown():
                  - Populates dropdown with student emails
            
            10. **Initialize Containers** (created later in get_view):
                a. Set form_container = None (created in get_view)
                b. Set manage_students_btn = None (created in get_view)

        Interactions:
            - **ft.TextField, ft.Dropdown, ft.DatePicker, etc.**: UI component creation
            - **student_manager.update_student_dropdown()**: Populates student dropdown
            - **Event handlers**: Registered for dropdowns, switch, pickers

        Example:
            >>> # After initialization
            >>> todo = TodoView(page, callback, drive)
            >>> # All components created and stored
            >>> print(todo.assignment_title.hint_text)
            Assignment Title
            >>> print(len(todo.subject_dropdown.options))
            8
            >>> print(todo.mode_switch.value)
            False
            >>> print(todo.assignment_column.scroll)
            auto

        See Also:
            - :meth:`__init__`: Calls this during initialization
            - :meth:`get_view`: Assembles components into layout
            - :meth:`switch_mode`: Handles mode switch events
            - :meth:`display_assignments`: Updates assignment_column

        Notes:
            - Components created but not attached to page yet
            - All components stored as instance attributes
            - Event handlers registered during creation
            - Dropdowns populated with predefined options
            - Student dropdown populated by student_manager
            - Form and manage button containers created later
            - Assignment column initially empty (populated by display_assignments)
            - Picker controls added to page overlay when needed
        """
        self.assignment_title = ft.TextField(hint_text="Assignment Title", expand=True)
        self.assignment_description = ft.TextField(
            hint_text="Description/Instructions",
            multiline=True,
            min_lines=3,
            max_lines=5,
            expand=True
        )
        
        self.subject_dropdown = ft.Dropdown(
            hint_text="Select Subject",
            options=[
                ft.dropdown.Option("Mathematics"),
                ft.dropdown.Option("Science"),
                ft.dropdown.Option("English"),
                ft.dropdown.Option("History"),
                ft.dropdown.Option("Computer Science"),
                ft.dropdown.Option("Arts"),
                ft.dropdown.Option("Physical Education"),
                ft.dropdown.Option("Other"),
            ],
            width=200
        )
        
        self.max_score_field = ft.TextField(
            hint_text="Max Score (e.g., 100)",
            width=150,
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.NumbersOnlyInputFilter()
        )
        
        self.target_dropdown = ft.Dropdown(
            hint_text="Assign To",
            width=200,
            value="all",
            options=[
                ft.dropdown.Option("all", "All Students"),
                ft.dropdown.Option("bridging", "Bridging Only"),
                ft.dropdown.Option("regular", "Regular Only"),
            ]
        )
        
        
        self.selected_drive_folder_id = None
        self.drive_folder_label = ft.Text("No folder selected", size=12, italic=True)
        

        self.attachment_text = ft.Text("No file attached", size=12, italic=True)
        self.selected_attachment = {"path": None, "name": None}
        
        self.selected_date_value = None
        self.selected_time_value = None
        self.selected_deadline_display = ft.Text("No deadline selected", size=12, italic=True)
        
        self.date_picker = ft.DatePicker(on_change=self.on_date_selected)
        self.time_picker = ft.TimePicker(on_change=self.on_time_selected)
        
        self.assignment_column = ft.Column(scroll="auto", expand=True, spacing=10)
        

        self.filter_dropdown = ft.Dropdown(
            hint_text="Filter",
            options=[
                ft.dropdown.Option("All"),
                ft.dropdown.Option("Active"),
                ft.dropdown.Option("Completed"),
                ft.dropdown.Option("Overdue"),
            ],
            value="All",
            width=150,
            on_change=lambda e: self.display_assignments()
        )
        

        self.mode_switch = ft.Switch(value=False, on_change=self.switch_mode)
        self.mode_label = ft.Text("👨‍🏫 Teacher View", size=16, weight=ft.FontWeight.BOLD)
        
        self.settings_btn = ft.ElevatedButton(
            "Storage",
            icon=ft.Icons.SETTINGS,
            on_click=lambda e: self.storage_manager.show_storage_settings()
        )
        
        self.student_dropdown = ft.Dropdown(
            hint_text="Select Student",
            width=250,
            on_change=self.on_student_selected
        )
        self.student_manager.update_student_dropdown()
        
        self.student_selector_row = ft.Row([
            ft.Text("Viewing as:", size=14),
            self.student_dropdown
        ], visible=False)
        
        self.form_container = None
        self.manage_students_btn = None
    
    def load_saved_links(self):
        """Load legacy saved link shortcuts from JSON file.

        Reads the saved_links.json file containing Drive folder shortcuts
        and returns the links list. This is a legacy feature maintained
        for backward compatibility.

        Returns:
            list: List of saved link dictionaries. Each link contains:
                - id (str): Drive folder/file ID
                - name (str): Display name for link
                - url (str): Full Drive URL
                Returns empty list if file doesn't exist or can't be parsed.

        Algorithm:
            1. **Check File Existence**:
               a. Check if SAVED_LINKS_FILE ("saved_links.json") exists
               b. Use os.path.exists() for file check
            
            2. **Load File** (if exists):
               a. Try to open file with UTF-8 encoding
               b. Parse JSON content with json.load()
               c. Extract "links" key from data dictionary
               d. Return links list
            
            3. **Handle Errors**:
               a. If any exception occurs (IOError, JSONDecodeError):
                  i. Catch exception silently
                  ii. Continue to return empty list
            
            4. **Return Default**:
               a. If file doesn't exist or error occurs:
                  i. Return empty list []

        Interactions:
            - **os.path.exists()**: Checks file existence
            - **json.load()**: Parses JSON content
            - **File I/O**: Reads from saved_links.json

        Example:
            >>> # File exists with data
            >>> links = todo_view.load_saved_links()
            >>> print(links)
            [
                {'id': '1abc...', 'name': 'Assignments', 'url': 'https://...'},
                {'id': '2def...', 'name': 'Resources', 'url': 'https://...'}
            ]
            >>> 
            >>> # File doesn't exist
            >>> links = todo_view.load_saved_links()
            >>> print(links)
            []

        See Also:
            - :meth:`__init__`: Calls this during initialization
            - :meth:`get_folder_name_by_id`: Uses saved links for name resolution

        Notes:
            - Legacy feature for Drive folder shortcuts
            - File stored in current working directory
            - Returns empty list on any error (graceful failure)
            - JSON structure: {"links": [{"id": ..., "name": ..., "url": ...}]}
            - Not actively used in new implementations
            - Maintained for backward compatibility
        """

        if os.path.exists(SAVED_LINKS_FILE):
            try:
                with open(SAVED_LINKS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("links", [])
            except:
                pass
        return []
    
    def get_folder_name_by_id(self, folder_id):
        """Resolve a Drive folder ID to its display name.

        Attempts to find the folder name by checking saved links first,
        then querying the Drive API if available. Provides fallback name
        if folder cannot be resolved.

        Args:
            folder_id (str): Google Drive folder ID to resolve. Example:
                '1abc...xyz' (33-character alphanumeric string).

        Returns:
            str: Resolved folder name. Returns folder's actual name if found,
                or "Linked Folder" if resolution fails.

        Algorithm:
            1. **Check Saved Links Cache**:
               a. Iterate through self.saved_links list
               b. For each link dictionary:
                  i. Check if link.get("id") == folder_id
                  ii. If match found:
                      - Return link.get("name", folder_id)
                      - Exits function immediately
            
            2. **Query Drive API** (if service available):
               a. Check if self.drive_service is not None
               b. If Drive service exists:
                  i. Try to call drive_service.get_file_info(folder_id)
                  ii. If info returned:
                      - Extract name: info.get('name', 'Linked Folder')
                      - Return folder name
                  iii. If exception occurs:
                       - Pass silently, continue to fallback
            
            3. **Return Fallback**:
               a. If no match in saved links and no Drive service:
                  i. Return "Linked Folder" as default name

        Interactions:
            - **saved_links**: Searches in-memory link cache
            - **DriveService.get_file_info()**: Queries Drive API for metadata
            - **Drive API**: Retrieves folder/file information

        Example:
            >>> # Folder in saved links
            >>> name = todo_view.get_folder_name_by_id('1abc...xyz')
            >>> print(name)
            Assignments Folder
            >>> 
            >>> # Folder not in links, query Drive
            >>> name = todo_view.get_folder_name_by_id('2def...uvw')
            >>> print(name)
            Project Resources
            >>> 
            >>> # Folder not found anywhere
            >>> name = todo_view.get_folder_name_by_id('invalid_id')
            >>> print(name)
            Linked Folder

        See Also:
            - :meth:`load_saved_links`: Loads saved links cache
            - :class:`~services.drive_service.DriveService`: Drive API wrapper

        Notes:
            - Two-tier lookup: saved links first, then Drive API
            - Saved links check is fast (in-memory)
            - Drive API call is slower (network request)
            - Gracefully handles missing Drive service
            - Gracefully handles API errors
            - Returns generic name if resolution fails
            - Used for displaying folder names in UI
        """
        for link in self.saved_links:
            if link.get("id") == folder_id:
                return link.get("name", folder_id)
        
        if self.drive_service:
            try:
                info = self.drive_service.get_file_info(folder_id)
                if info:
                    return info.get('name', 'Linked Folder')
            except:
                pass
        
        return "Linked Folder"
    
    def on_date_selected(self, e):
        """Handle date picker selection event.

        Updates the selected date value, refreshes the deadline display,
        closes the date picker, and immediately opens the time picker for
        completing the deadline selection.

        Args:
            e (ft.ControlEvent): Date picker change event. Not used directly
                but required by Flet event handler signature.

        Returns:
            None: Updates state and UI as side effects.

        Algorithm:
            1. **Store Selected Date**:
               a. Access self.date_picker.value (datetime.date object)
               b. Assign to self.selected_date_value
            
            2. **Update Display**:
               a. Call self.update_deadline_display()
               b. Updates selected_deadline_display text with new date
            
            3. **Close Date Picker**:
               a. Call self.page.close(self.date_picker)
               b. Removes date picker from page overlay
            
            4. **Open Time Picker**:
               a. Call self.page.open(self.time_picker)
               b. Adds time picker to page overlay
               c. User continues deadline selection with time
            
            5. **Refresh UI**:
               a. Call self.page.update()
               b. Renders all changes

        Interactions:
            - **ft.DatePicker**: Reads selected value
            - **update_deadline_display()**: Updates display text
            - **ft.Page**: Closes date picker, opens time picker

        Example:
            >>> # User selects December 31, 2025
            >>> todo_view.on_date_selected(event)
            >>> # selected_date_value = date(2025, 12, 31)
            >>> # Display: "Deadline: 2025-12-31"
            >>> # Date picker closes
            >>> # Time picker opens

        See Also:
            - :meth:`on_time_selected`: Handles time selection
            - :meth:`update_deadline_display`: Updates deadline text
            - :attr:`date_picker`: Date picker control
            - :attr:`time_picker`: Time picker control

        Notes:
            - Part of two-step deadline selection process
            - Date picker auto-closes after selection
            - Time picker auto-opens for seamless UX
            - Event parameter required but unused
            - Display updates immediately
        """
        self.selected_date_value = self.date_picker.value
        self.update_deadline_display()
        self.page.close(self.date_picker)
        self.page.open(self.time_picker)
        self.page.update()
    
    def on_time_selected(self, e):
        """Handle time picker selection event.

        Updates the selected time value, refreshes the deadline display,
        and closes the time picker to complete the deadline selection process.

        Args:
            e (ft.ControlEvent): Time picker change event. Not used directly
                but required by Flet event handler signature.

        Returns:
            None: Updates state and UI as side effects.

        Algorithm:
            1. **Store Selected Time**:
               a. Access self.time_picker.value (datetime.time object)
               b. Assign to self.selected_time_value
            
            2. **Update Display**:
               a. Call self.update_deadline_display()
               b. Updates selected_deadline_display with date and time
            
            3. **Close Time Picker**:
               a. Call self.page.close(self.time_picker)
               b. Removes time picker from page overlay
            
            4. **Refresh UI**:
               a. Call self.page.update()
               b. Renders all changes

        Interactions:
            - **ft.TimePicker**: Reads selected value
            - **update_deadline_display()**: Updates display text
            - **ft.Page**: Closes time picker, updates UI

        Example:
            >>> # User selects 11:59 PM
            >>> todo_view.on_time_selected(event)
            >>> # selected_time_value = time(23, 59)
            >>> # Display: "Deadline: 2025-12-31 at 23:59:00"
            >>> # Time picker closes

        See Also:
            - :meth:`on_date_selected`: Handles date selection
            - :meth:`update_deadline_display`: Updates deadline text
            - :attr:`time_picker`: Time picker control

        Notes:
            - Completes two-step deadline selection
            - Time picker auto-closes after selection
            - Display shows complete date and time
            - Event parameter required but unused
        """
        self.selected_time_value = self.time_picker.value
        self.update_deadline_display()
        self.page.close(self.time_picker)
        self.page.update()
    
    def update_deadline_display(self):
        """Update the UI text showing the selected deadline.

        Formats and displays the deadline based on currently selected
        date and time values. Shows partial deadline if only date selected.

        Returns:
            None: Updates selected_deadline_display.value as side effect.

        Algorithm:
            1. **Check Both Values Available**:
               a. If selected_date_value AND selected_time_value:
                  i. Format: "Deadline: {date} at {time}"
                  ii. Update selected_deadline_display.value
                  iii. Complete deadline shown
            
            2. **Check Only Date Available**:
               a. Elif selected_date_value only:
                  i. Format: "Deadline: {date}"
                  ii. Update selected_deadline_display.value
                  iii. Time not yet selected
            
            3. **No Selection**:
               a. Else (neither selected):
                  i. Set value: "No deadline selected"
                  ii. Default state

        Interactions:
            - **selected_date_value**: Reads date attribute
            - **selected_time_value**: Reads time attribute
            - **selected_deadline_display**: Updates text value

        Example:
            >>> # Both date and time selected
            >>> todo_view.selected_date_value = date(2025, 12, 31)
            >>> todo_view.selected_time_value = time(23, 59)
            >>> todo_view.update_deadline_display()
            >>> print(todo_view.selected_deadline_display.value)
            Deadline: 2025-12-31 at 23:59:00
            >>> 
            >>> # Only date selected
            >>> todo_view.selected_time_value = None
            >>> todo_view.update_deadline_display()
            >>> print(todo_view.selected_deadline_display.value)
            Deadline: 2025-12-31
            >>> 
            >>> # Nothing selected
            >>> todo_view.selected_date_value = None
            >>> todo_view.update_deadline_display()
            >>> print(todo_view.selected_deadline_display.value)
            No deadline selected

        See Also:
            - :meth:`on_date_selected`: Calls this after date selection
            - :meth:`on_time_selected`: Calls this after time selection
            - :attr:`selected_deadline_display`: Display text control

        Notes:
            - Called automatically after date/time picker selections
            - Handles partial deadline (date only)
            - Formats datetime objects as strings
            - Display text automatically updates in UI
        """
        if self.selected_date_value and self.selected_time_value:
            self.selected_deadline_display.value = f"Deadline: {self.selected_date_value} at {self.selected_time_value}"
        elif self.selected_date_value:
            self.selected_deadline_display.value = f"Deadline: {self.selected_date_value}"
        else:
            self.selected_deadline_display.value = "No deadline selected"
    
    def pick_file(self, e):
        """Open file picker dialog for attaching a local file to assignment.

        Creates and displays a file picker dialog, captures the selected file
        path and name, and updates the attachment display text.

        Args:
            e (ft.ControlEvent): Button click event. Not used directly but
                required by Flet event handler signature.

        Returns:
            None: Updates selected_attachment dict and UI as side effects.

        Algorithm:
            1. **Define Result Callback**:
               a. Define inner function on_result(e: FilePickerResultEvent)
               b. Callback executes when user selects file
               c. Implementation:
                  i. Check if e.files is not empty
                  ii. If files selected:
                      - Store e.files[0].path in selected_attachment["path"]
                      - Store e.files[0].name in selected_attachment["name"]
                      - Update attachment_text.value = "📎 {filename}"
                      - Call page.update() to render changes
            
            2. **Create File Picker**:
               a. Instantiate ft.FilePicker(on_result=on_result)
               b. File picker configured with result callback
            
            3. **Add to Page Overlay**:
               a. Append file_picker to page.overlay list
               b. Makes picker available for display
            
            4. **Update Page**:
               a. Call page.update() to register picker
            
            5. **Show File Picker**:
               a. Call file_picker.pick_files()
               b. Opens system file selection dialog
               c. User selects file
               d. on_result callback executes with selection

        Interactions:
            - **ft.FilePicker**: Creates and displays file selection dialog
            - **ft.Page.overlay**: Registers picker with page
            - **selected_attachment**: Updates with file info
            - **attachment_text**: Updates display text

        Example:
            >>> # User clicks "Attach File" button
            >>> todo_view.pick_file(click_event)
            >>> # File picker opens
            >>> # User selects "homework.pdf"
            >>> print(todo_view.selected_attachment)
            {'path': '/path/to/homework.pdf', 'name': 'homework.pdf'}
            >>> print(todo_view.attachment_text.value)
            📎 homework.pdf

        See Also:
            - :meth:`get_view`: Creates "Attach File" button
            - :class:`ft.FilePicker`: Flet file picker component

        Notes:
            - File picker opens system-native dialog
            - Only one file can be selected at a time
            - File not uploaded until assignment created
            - Attachment info stored in selected_attachment dict
            - Display text shows file name with paperclip emoji
            - Event parameter required but unused
        """
        def on_result(e: ft.FilePickerResultEvent):
            if e.files:
                self.selected_attachment["path"] = e.files[0].path
                self.selected_attachment["name"] = e.files[0].name
                self.attachment_text.value = f"📎 {e.files[0].name}"
                self.page.update()
        
        file_picker = ft.FilePicker(on_result=on_result)
        self.page.overlay.append(file_picker)
        self.page.update()
        file_picker.pick_files()
    
    def display_assignments(self):
        """Render the list of assignments based on current mode and filters.

        Clears the assignment column and delegates rendering to the appropriate
        manager method based on whether the user is in teacher or student mode.

        Returns:
            None: Updates assignment_column.controls and page as side effects.

        Algorithm:
            1. **Clear Assignment Display**:
               a. Access self.assignment_column.controls
               b. Call clear() to remove all existing cards
            
            2. **Check Current Mode**:
               a. If self.current_mode == "teacher":
                  i. Call assignment_manager.display_teacher_view()
                  ii. Manager shows all assignments with edit/delete
               b. Else (student mode):
                  i. Call assignment_manager.display_student_view()
                  ii. Manager shows assigned assignments with submit buttons
            
            3. **Refresh UI**:
               a. Call self.page.update()
               b. Renders updated assignment_column

        Interactions:
            - **assignment_column**: Clears controls list
            - **AssignmentManager.display_teacher_view()**: Renders teacher view
            - **AssignmentManager.display_student_view()**: Renders student view
            - **ft.Page.update()**: Renders changes

        Example:
            >>> # Display in teacher mode
            >>> todo_view.current_mode = "teacher"
            >>> todo_view.display_assignments()
            >>> # Shows all assignments with edit/delete buttons
            >>> 
            >>> # Display in student mode
            >>> todo_view.current_mode = "student"
            >>> todo_view.current_student_email = "student@example.com"
            >>> todo_view.display_assignments()
            >>> # Shows assignments for selected student with submit buttons

        See Also:
            - :meth:`switch_mode`: Calls this after mode change
            - :class:`~ui.todo_modules.assignment_manager.AssignmentManager`: Handles rendering
            - :attr:`assignment_column`: Container for assignment cards

        Notes:
            - Called automatically after mode switch
            - Called after filter dropdown change
            - Delegation pattern - manager handles actual rendering
            - Assignment column cleared before repopulation
            - Manager accesses self.assignments for data
            - Manager creates assignment cards dynamically
        """
        self.assignment_column.controls.clear()
        
        if self.current_mode == "teacher":
            self.assignment_manager.display_teacher_view()
        else:
            self.assignment_manager.display_student_view()
        
        self.page.update()
    
    def switch_mode(self, e):
        """Toggle between Teacher and Student view modes.

        Switches the application mode based on the mode switch control,
        updates UI element visibility for role-specific features, and
        refreshes the assignment display.

        Args:
            e (ft.ControlEvent): Switch toggle event. Not used directly but
                required by Flet event handler signature.

        Returns:
            None: Updates mode, UI visibility, and display as side effects.

        Algorithm:
            1. **Update Mode State**:
               a. Check self.mode_switch.value (True/False)
               b. If True:
                  i. Set self.current_mode = "student"
               c. If False:
                  i. Set self.current_mode = "teacher"
            
            2. **Configure Student Mode** (if student):
               a. Set mode_label.value = "👨‍🎓 Student View"
               b. Set student_selector_row.visible = True
                  - Shows student dropdown
               c. If form_container exists:
                  i. Set form_container.visible = False
                  ii. Hides assignment creation form
               d. If manage_students_btn exists:
                  i. Set manage_students_btn.visible = False
                  ii. Hides student management button
            
            3. **Configure Teacher Mode** (else teacher):
               a. Set mode_label.value = "👨‍🏫 Teacher View"
               b. Set student_selector_row.visible = False
                  - Hides student dropdown
               c. If form_container exists:
                  i. Set form_container.visible = True
                  ii. Shows assignment creation form
               d. If manage_students_btn exists:
                  i. Set manage_students_btn.visible = True
                  ii. Shows student management button
            
            4. **Refresh Assignment Display**:
               a. Call self.display_assignments()
               b. Updates assignment list for current mode
            
            5. **Update Page**:
               a. Call self.page.update()
               b. Renders all visibility changes

        Interactions:
            - **mode_switch**: Reads toggle value
            - **mode_label**: Updates text and emoji
            - **student_selector_row**: Shows/hides student selector
            - **form_container**: Shows/hides assignment form
            - **manage_students_btn**: Shows/hides management button
            - **display_assignments()**: Refreshes assignment list

        Example:
            >>> # Switch to student mode
            >>> todo_view.mode_switch.value = True
            >>> todo_view.switch_mode(event)
            >>> print(todo_view.current_mode)
            student
            >>> print(todo_view.mode_label.value)
            👨‍🎓 Student View
            >>> print(todo_view.student_selector_row.visible)
            True
            >>> print(todo_view.form_container.visible)
            False
            >>> 
            >>> # Switch back to teacher mode
            >>> todo_view.mode_switch.value = False
            >>> todo_view.switch_mode(event)
            >>> print(todo_view.current_mode)
            teacher
            >>> print(todo_view.mode_label.value)
            👨‍🏫 Teacher View
            >>> print(todo_view.form_container.visible)
            True

        See Also:
            - :meth:`display_assignments`: Refreshes display after switch
            - :meth:`on_student_selected`: Handles student selection in student mode
            - :attr:`mode_switch`: Switch control

        Notes:
            - Mode switch control is a toggle (True/False)
            - Student mode: read-only view of assigned work
            - Teacher mode: full CRUD operations on assignments
            - UI elements show/hide based on mode
            - Assignment display updates automatically
            - Event parameter required but unused
        """
        self.current_mode = "student" if self.mode_switch.value else "teacher"
        if self.current_mode == "student":
            self.mode_label.value = "👨‍🎓 Student View"
            self.student_selector_row.visible = True
            if self.form_container:
                self.form_container.visible = False
            if self.manage_students_btn:
                self.manage_students_btn.visible = False
        else:
            self.mode_label.value = "👨‍🏫 Teacher View"
            self.student_selector_row.visible = False
            if self.form_container:
                self.form_container.visible = True
            if self.manage_students_btn:
                self.manage_students_btn.visible = True
        self.display_assignments()
        self.page.update()
    
    def on_student_selected(self, e):
        """Handle student selection change in student dropdown.

        Processes student dropdown selection, triggering registration dialog
        if the special registration option is selected, or updating the current
        student and refreshing the assignment display.

        Args:
            e (ft.ControlEvent): Dropdown change event. Not used directly but
                required by Flet event handler signature.

        Returns:
            None: Updates current_student_email and display as side effects.

        Algorithm:
            1. **Check for Registration Option**:
               a. If student_dropdown.value == "__register__":
                  i. Set student_dropdown.value = None (clear selection)
                  ii. Call student_manager.register_student_dialog()
                  iii. Opens dialog for new student registration
                  iv. Return early (exit function)
            
            2. **Update Current Student**:
               a. Assign student_dropdown.value to current_student_email
               b. Stores selected student's email
            
            3. **Refresh Assignment Display**:
               a. Call self.display_assignments()
               b. Shows assignments for newly selected student

        Interactions:
            - **student_dropdown**: Reads selected value
            - **student_manager.register_student_dialog()**: Opens registration
            - **current_student_email**: Updates with selection
            - **display_assignments()**: Refreshes display

        Example:
            >>> # User selects a student
            >>> todo_view.student_dropdown.value = "student@example.com"
            >>> todo_view.on_student_selected(event)
            >>> print(todo_view.current_student_email)
            student@example.com
            >>> # Assignments refresh to show student's work
            >>> 
            >>> # User selects registration option
            >>> todo_view.student_dropdown.value = "__register__"
            >>> todo_view.on_student_selected(event)
            >>> # Registration dialog opens
            >>> print(todo_view.student_dropdown.value)
            None

        See Also:
            - :class:`~ui.todo_modules.student_manager.StudentManager`: Handles registration
            - :meth:`display_assignments`: Refreshes assignment list
            - :attr:`student_dropdown`: Student selector control

        Notes:
            - Special value "__register__" triggers registration dialog
            - Dropdown cleared after selecting registration option
            - current_student_email used by display_assignments to filter
            - Event parameter required but unused
        """
        if self.student_dropdown.value == "__register__":
            self.student_dropdown.value = None
            self.student_manager.register_student_dialog()
            return
        self.current_student_email = self.student_dropdown.value
        self.display_assignments()
    
    def show_overlay(self, content, title=None, width=400, height=None):
        """Display a modal overlay dialog with custom content.

        Creates and shows a centered modal dialog containing the provided
        content control. Supports custom title, dimensions, and scrollable
        content. Returns both the overlay control and a close function.

        Args:
            content (ft.Control): The primary content widget to display in
                dialog body. Can be any Flet control (Column, Container, etc.).
            title (str, optional): Title text displayed in dialog header.
                If None, no title shown. Defaults to None.
            width (int, optional): Dialog width in pixels. Defaults to 400.
            height (int, optional): Dialog height in pixels. If provided and
                content is scrollable Column, wraps content in container with
                height constraint. Defaults to None (auto-height).

        Returns:
            tuple: A 2-tuple containing:
                - overlay (ft.Container): The overlay control added to page.
                - close_overlay (Callable): Function to close the overlay.
                  Signature: (e) -> None. Call with None or event object.

        Algorithm:
            1. **Define Close Function**:
               a. Create close_overlay(e) function
               b. Implementation:
                  i. Check if overlay in page.overlay list
                  ii. If present, remove overlay
                  iii. Call page.update()
            
            2. **Build Header Controls**:
               a. Create empty list header_controls
               b. If title provided:
                  i. Create Text with title, size 20, bold
                  ii. Set overflow VISIBLE, no_wrap False, expand True
                  iii. Append to header_controls
               c. Create IconButton with CLOSE icon
               d. Set on_click to close_overlay
               e. Append close button to header_controls
            
            3. **Wrap Content** (if height specified):
               a. If height AND content is scrollable Column:
                  i. Wrap content in Container
                  ii. Set expand=True, padding=10
                  iii. Store in content_wrapper
               b. Else:
                  i. Use content as-is (content_wrapper = content)
            
            4. **Build Overlay Content**:
               a. Create Column with:
                  i. Row(header_controls) - title and close button
                  ii. Divider - separator line
                  iii. content_wrapper - main content
               b. Set tight=True, spacing=10
               c. Set expand=True if height specified
            
            5. **Build Inner Container**:
               a. Create Container with:
                  i. content=overlay_content
                  ii. padding=20, bgcolor=WHITE
                  iii. border_radius=10
                  iv. width=width, height=height (if specified)
                  v. shadow with blur_radius=20
            
            6. **Build Outer Overlay**:
               a. Create Container with:
                  i. content=inner_container
                  ii. alignment=center
                  iii. expand=True
                  iv. bgcolor=semi-transparent black (0.5 opacity)
                  v. on_click=lambda e: None (prevents click-through)
            
            7. **Display Overlay**:
               a. Append overlay to page.overlay list
               b. Call page.update()
            
            8. **Return Tuple**:
               a. Return (overlay, close_overlay)
               b. Caller can close by calling close_overlay(None)

        Interactions:
            - **ft.Container**: Creates overlay structure
            - **ft.Column, ft.Row**: Arranges header and content
            - **ft.Text, ft.IconButton**: Header components
            - **ft.Page.overlay**: Adds/removes overlay

        Example:
            >>> # Simple dialog
            >>> content = ft.Column([
            ...     ft.Text("Are you sure?"),
            ...     ft.Row([
            ...         ft.TextButton("Cancel", on_click=lambda e: close_fn(e)),
            ...         ft.ElevatedButton("Confirm", on_click=handle_confirm)
            ...     ])
            ... ])
            >>> overlay, close_fn = todo_view.show_overlay(
            ...     content,
            ...     title="Confirm Delete",
            ...     width=300
            ... )
            >>> 
            >>> # Scrollable dialog with height
            >>> long_content = ft.Column([...], scroll="auto")
            >>> overlay, close_fn = todo_view.show_overlay(
            ...     long_content,
            ...     title="View Details",
            ...     width=500,
            ...     height=600
            ... )
            >>> 
            >>> # Close dialog programmatically
            >>> close_fn(None)

        See Also:
            - :meth:`show_snackbar`: Alternative for brief notifications
            - :class:`~ui.todo_modules.assignment_manager.AssignmentManager`: Uses this for dialogs
            - :class:`~ui.todo_modules.student_manager.StudentManager`: Uses this for dialogs

        Notes:
            - Modal overlay blocks interaction with page content
            - Semi-transparent black background (50% opacity)
            - Close button always shown in header
            - Content can be any Flet control
            - Scrollable columns automatically wrapped if height specified
            - Shadow effect adds depth to dialog
            - Click on overlay background doesn't close (must use close button)
            - Multiple overlays can be shown (stacked)
        """
        def close_overlay(e):
            if overlay in self.page.overlay:
                self.page.overlay.remove(overlay)
                self.page.update()
        
        header_controls = []
        if title:
            header_controls.append(
                ft.Text(
                    title, 
                    size=20, 
                    weight=ft.FontWeight.BOLD,
                    overflow=ft.TextOverflow.VISIBLE,
                    no_wrap=False,
                    expand=True
                )
            )
        
        header_controls.append(ft.IconButton(icon=ft.Icons.CLOSE, on_click=close_overlay))
        
        if height and isinstance(content, ft.Column) and content.scroll:
            content_wrapper = ft.Container(
                content=content,
                expand=True,
                padding=10
            )
        else:
            content_wrapper = content
        
        overlay_content = ft.Column([
            ft.Row(header_controls, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            content_wrapper
        ], tight=True, spacing=10, expand=True if height else False)
        
        overlay = ft.Container(
            content=ft.Container(
                content=overlay_content,
                padding=20,
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                width=width,
                height=height,
                shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK))
            ),
            alignment=ft.alignment.center,
            expand=True,
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
            on_click=lambda e: None
        )
        
        self.page.overlay.append(overlay)
        self.page.update()
        return overlay, close_overlay

    def get_view(self):
        """Construct and return the complete TodoView UI layout.

        Builds the entire LMS interface by assembling UI components into a
        structured layout. Creates role-specific elements (forms, buttons)
        based on current mode and arranges all components in a scrollable
        column layout.

        Returns:
            ft.Column: Root control containing the complete TodoView layout.
                Structure: Column[header, mode_controls, student_selector,
                form, divider, assignment_list]. Scrollable and expands to
                fill available space.

        Algorithm:
            1. **Display Initial Assignments**:
               a. Call self.display_assignments()
               b. Populates assignment_column with cards
            
            2. **Create Action Buttons**:
               a. Create attach_btn ElevatedButton:
                  - Text: "📎 Attach File"
                  - on_click: pick_file
                  - icon: ATTACH_FILE
               b. Create pick_deadline_btn ElevatedButton:
                  - Text: "📅 Set Deadline"
                  - on_click: open date_picker
                  - icon: CALENDAR_MONTH
               c. Create add_btn ElevatedButton:
                  - Text: "➕ Add Assignment"
                  - on_click: assignment_manager.add_assignment
                  - icon: ADD
                  - style: blue background, white text
            
            3. **Build Assignment Form Container**:
               a. Create form_container Container with:
                  i. Column containing:
                     - Text("Create New Assignment", size 20, bold)
                     - assignment_title field
                     - Row[subject_dropdown, max_score_field, target_dropdown]
                     - assignment_description field
                     - Row[Drive folder display and picker]
                     - Row[attach_btn, attachment_text]
                     - Row[pick_deadline_btn, deadline_display]
                     - Spacing container
                     - add_btn
                  ii. padding=20, border_radius=10
                  iii. bgcolor=light blue-grey (0.05 opacity)
               b. Set visible based on current_mode == "teacher"
               c. Store in self.form_container
            
            4. **Create Back Button** (if on_back provided):
               a. If self.on_back exists:
                  i. Create IconButton with ARROW_BACK icon
                  ii. on_click: lambda e: on_back()
                  iii. tooltip: "Back to Dashboard"
               b. Else:
                  i. Create empty Container
            
            5. **Create Manage Students Button**:
               a. Create ElevatedButton:
                  - Text: "👥 Manage Students"
                  - on_click: student_manager.manage_students_dialog
                  - icon: PEOPLE
               b. Set visible based on current_mode == "teacher"
               c. Store in self.manage_students_btn
            
            6. **Build Header Section**:
               a. Create Container with Row containing:
                  i. back_btn (if available)
                  ii. Icon(SCHOOL, size 40, blue)
                  iii. Text("Learning Management System", size 28, bold)
               b. Set padding=20
            
            7. **Build Mode Controls Section**:
               a. Create Container with Row containing:
                  i. mode_label (Teacher/Student View)
                  ii. mode_switch (toggle control)
                  iii. settings_btn (Storage button)
                  iv. Expanded container (pushes next item right)
                  v. manage_students_btn (teacher only)
               b. Set padding=10, light blue background, border_radius=10
            
            8. **Build Assignment List Section**:
               a. Create Container with Column containing:
                  i. Row with:
                      - Text("Assignments", size 20, bold, expand)
                      - filter_dropdown
                  ii. Container with assignment_column (expand=True)
               b. Set expand=True for vertical fill
            
            9. **Assemble Complete Layout**:
               a. Create root Column with:
                  i. Header container
                  ii. Mode controls container
                  iii. student_selector_row (student mode only)
                  iv. form_container (teacher mode only)
                  v. Divider (height=20)
                  vi. Assignment list container (expanded)
               b. Set expand=True, scroll="auto"
            
            10. **Return Layout**:
                a. Return assembled Column control

        Interactions:
            - **display_assignments()**: Populates assignment list
            - **assignment_manager.add_assignment**: Creates new assignment
            - **student_manager.manage_students_dialog**: Opens student management
            - **storage_manager.open_new_assignment_folder_picker**: Opens folder picker
            - **pick_file()**: Opens file picker
            - **page.open()**: Opens date/time pickers

        Example:
            >>> # Build and display view
            >>> layout = todo_view.get_view()
            >>> page.add(layout)
            >>> page.update()
            >>> 
            >>> # Layout structure:
            >>> # ┌─ Header ──────────────────────┐
            >>> # │ ← [School Icon] LMS           │
            >>> # ├─ Mode Controls ───────────────┤
            >>> # │ 👨‍🏫 Teacher View [Toggle] Storage │
            >>> # ├─ Assignment Form ─────────────┤
            >>> # │ Create New Assignment         │
            >>> # │ [Title Field]                 │
            >>> # │ [Subject] [Score] [Target]    │
            >>> # │ [Description]                 │
            >>> # │ [📎 Attach] [📅 Deadline]      │
            >>> # │ [➕ Add Assignment]            │
            >>> # ├─ Assignment List ─────────────┤
            >>> # │ Assignments      [Filter]     │
            >>> # │ [Assignment Card 1]           │
            >>> # │ [Assignment Card 2]           │
            >>> # └───────────────────────────────┘

        See Also:
            - :meth:`__init__`: Initializes components used in layout
            - :meth:`_init_ui_components`: Creates UI controls
            - :meth:`display_assignments`: Populates assignment list
            - :meth:`switch_mode`: Handles mode changes

        Notes:
            - Layout is scrollable (handles long content)
            - Form visible only in teacher mode
            - Student selector visible only in student mode
            - Back button conditional on on_back callback
            - All components created in _init_ui_components
            - Assignment column populated by display_assignments
            - Layout expands to fill available vertical space
            - Responsive design with proper spacing
        """
        self.display_assignments()
        
        attach_btn = ft.ElevatedButton(
            "📎 Attach File",
            on_click=self.pick_file,
            icon=ft.Icons.ATTACH_FILE
        )
        
        pick_deadline_btn = ft.ElevatedButton(
            "📅 Set Deadline",
            on_click=lambda e: self.page.open(self.date_picker),
            icon=ft.Icons.CALENDAR_MONTH
        )
        
        add_btn = ft.ElevatedButton(
            "➕ Add Assignment",
            on_click=self.assignment_manager.add_assignment,
            icon=ft.Icons.ADD,
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE)
        )
        
        self.form_container = ft.Container(
            content=ft.Column([
                ft.Text("Create New Assignment", size=20, weight=ft.FontWeight.BOLD),
                self.assignment_title,
                ft.Row([self.subject_dropdown, self.max_score_field, self.target_dropdown]),
                self.assignment_description,
                ft.Row([
                    ft.Text("Link to Drive:", size=14),
                    self.drive_folder_label,
                    ft.IconButton(
                        ft.Icons.FOLDER_OPEN,
                        tooltip="Select Drive Folder",
                        on_click=self.storage_manager.open_new_assignment_folder_picker
                    )
                ], spacing=10),
                ft.Row([attach_btn, self.attachment_text], spacing=10),
                ft.Row([
                    pick_deadline_btn, 
                    ft.Container(
                        content=self.selected_deadline_display,
                        padding=ft.padding.symmetric(horizontal=10, vertical=5),
                        border_radius=5,
                    )
                ], spacing=10),
                ft.Container(height=10),
                add_btn,
            ], spacing=10),
            padding=20,
            border_radius=10,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLUE_GREY),
            visible=self.current_mode == "teacher"
        )
        
        back_btn = ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            on_click=lambda e: self.on_back() if self.on_back else None,
            tooltip="Back to Dashboard"
        ) if self.on_back else ft.Container()
        
        self.manage_students_btn = ft.ElevatedButton(
            "👥 Manage Students",
            on_click=self.student_manager.manage_students_dialog,
            icon=ft.Icons.PEOPLE,
            visible=self.current_mode == "teacher"
        )
        
        return ft.Column([
            ft.Container(
                content=ft.Row([
                    back_btn,
                    ft.Icon(ft.Icons.SCHOOL, size=40, color=ft.Colors.BLUE),
                    ft.Text("Learning Management System", size=28, weight=ft.FontWeight.BOLD, expand=True, overflow=ft.TextOverflow.VISIBLE, no_wrap=False),
                ], alignment=ft.MainAxisAlignment.START),
                padding=20
            ),
            
            ft.Container(
                content=ft.Row([
                    self.mode_label,
                    self.mode_switch,
                    self.settings_btn,
                    ft.Container(expand=True),
                    self.manage_students_btn,
                    
                ]),
                padding=10,
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLUE),
                border_radius=10,
            ),
            
            self.student_selector_row,
            self.form_container,
            ft.Divider(height=20),
            
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Assignments", size=20, weight=ft.FontWeight.BOLD, expand=True),
                        self.filter_dropdown
                    ]),
                    ft.Container(content=self.assignment_column, expand=True)
                ], spacing=10),
                expand=True
            )
        ], 
        expand=True,
        scroll="auto")