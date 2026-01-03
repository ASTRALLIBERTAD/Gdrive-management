"""Assignment Manager Module.

This module handles the core logic for creating, displaying, editing, and managing
assignments within the LMS. It controls the generation of UI cards for both
teacher and student views and manages interaction with the Drive backend for
file attachments.

Classes:
    AssignmentManager: Manages assignment lifecycle and UI representation.
"""

import flet as ft
import datetime

from utils.common import open_drive_file, open_url, show_snackbar


class AssignmentManager:
    """Manages assignment creation, display, and modification.

    Purpose / Responsibility:
        Central controller for the assignment lifecycle. It handles user input for creating assignments,
        validates deadlines, renders role-specific UI (teacher vs student), coordinates with
        Drive storage, and manages notifications.

    Attributes:
        todo (TodoView): Reference to the main TodoView instance for collecting input and updating UI.
        file_preview (FilePreviewService): Service for generating file previews (optional integration).

    Interactions / Calls:
        - Interacts with `src.ui.todo_view.TodoView` (parent).
        - Calls `src.ui.todo_modules.data_manager.DataManager`.
        - Calls `src.ui.todo_modules.storage_manager.StorageManager`.
        - Calls `src.ui.todo_modules.submission_manager.SubmissionManager`.
        - Uses `src.services.file_preview_service.FilePreviewService`.

    Algorithm / Pseudocode:
        1. Initialize with reference to parent view.
        2. `add_assignment`: Validate form, upload file (if any), save, notify.
        3. `display_teacher_view`: Show list with management controls.
        4. `display_student_view`: Show list with submission status and filtering.
        5. `edit_assignment_dialog`: Modal for updating existing assignments.

    See Also:
        - :class:`~src.ui.todo_view.TodoView`
        - :class:`~src.ui.todo_modules.data_manager.DataManager`
    """
    
    def __init__(self, todo_view):
        """Initialize the AssignmentManager.

        Purpose:
            Sets up the manager with access to the parent view and initializes services.

        Args:
            todo_view (TodoView): Parent view instance for accessing shared state.

        Interactions:
            - Stores `todo_view` reference.
            - Initializes `FilePreviewService` (conditional import).
        """
        self.todo = todo_view
        
        try:
            from services.file_preview_service import FilePreviewService
            self.file_preview = FilePreviewService(todo_view.page, todo_view.drive_service)
        except ImportError:
            self.file_preview = None
    
    def add_assignment(self, e):
        """Handle the creation of a new assignment.

        Purpose:
            Validates inputs, processes file uploads, creates assignment record, saves to DB, and notifies students.

        Args:
            e (ft.ControlEvent): Trigger event (usually 'Create' button click).

        Interactions:
            - Reads inputs from `todo` fields (title, desc, subject, deadline, attachment).
            - Calls `storage_manager.upload_assignment_attachment`.
            - Calls `data_manager.save_assignments`.
            - Calls `notification_service.notify_new_assignment`.

        Algorithm:
            1. Extract values from UI fields.
            2. Validate: Title required, Subject required, Deadline must be future.
            3. If invalid -> `show_validation_errors`, exit.
            4. Create assignment dictionary (ID, timestamps, status).
            5. File Handling:
               a. If attachment selected: Call `upload_assignment_attachment`.
               b. Update assignment dict with upload result (Drive ID, link).
            6. Append to `todo.assignments`.
            7. Save to persistent storage.
            8. Send notifications to students.
            9. Reset form and refresh display.
        """
        title = self.todo.assignment_title.value.strip() if self.todo.assignment_title.value else ""
        description = self.todo.assignment_description.value.strip() if self.todo.assignment_description.value else ""
        subject = self.todo.subject_dropdown.value
        max_score = self.todo.max_score_field.value.strip() if self.todo.max_score_field.value else ""
        drive_folder_id = self.todo.selected_drive_folder_id
        target_for = self.todo.target_dropdown.value or "all"
        
        errors = []
        
        if not title:
            errors.append("Assignment title is required")
            self.todo.assignment_title.error_text = "Required"
            self.todo.assignment_title.border_color = ft.Colors.RED
        else:
            self.todo.assignment_title.error_text = None
            self.todo.assignment_title.border_color = None
        
        if not subject:
            errors.append("Subject must be selected")
            self.todo.subject_dropdown.error_text = "Required"
            self.todo.subject_dropdown.border_color = ft.Colors.RED
        else:
            self.todo.subject_dropdown.error_text = None
            self.todo.subject_dropdown.border_color = None
        
        final_deadline = None
        if self.todo.selected_date_value and self.todo.selected_time_value:
            final_deadline = datetime.datetime.combine(
                self.todo.selected_date_value,
                self.todo.selected_time_value
            )
        elif self.todo.selected_date_value:
            final_deadline = datetime.datetime.combine(
                self.todo.selected_date_value,
                datetime.time(23, 59)
            )
        
        if final_deadline:
            now = datetime.datetime.now()
            if final_deadline <= now:
                time_diff = now - final_deadline
                hours_ago = time_diff.total_seconds() / 3600
                
                if hours_ago < 1:
                    minutes_ago = time_diff.total_seconds() / 60
                    time_ago_str = f"{int(minutes_ago)} minutes ago"
                elif hours_ago < 24:
                    time_ago_str = f"{int(hours_ago)} hours ago"
                else:
                    days_ago = time_diff.days
                    time_ago_str = f"{days_ago} days ago"
                
                errors.append(f"⏰ Deadline is in the past ({time_ago_str})")
                
                self.todo.selected_deadline_display.value = f"Invalid: {time_ago_str}"
                self.todo.selected_deadline_display.color = ft.Colors.RED
            else:

                deadline_str = final_deadline.strftime('%B %d, %Y at %I:%M %p')
                self.todo.selected_deadline_display.value = f"✓ Deadline: {deadline_str}"
                self.todo.selected_deadline_display.color = ft.Colors.GREEN
        else:
            deadline_str = "No deadline"
            self.todo.selected_deadline_display.value = "No deadline selected"
            self.todo.selected_deadline_display.color = None
        
        if errors:
            self.show_validation_errors(errors)
            self.todo.page.update()
            return
        
        new_assignment = {
            'id': str(datetime.datetime.now().timestamp()),
            'title': title,
            'description': description,
            'subject': subject or 'Other',
            'deadline': final_deadline.isoformat() if final_deadline else None,
            'max_score': max_score or '100',
            'attachment': self.todo.selected_attachment["name"],
            'attachment_file_id': None,
            'attachment_file_link': None,
            'drive_folder_id': drive_folder_id,
            'target_for': target_for,
            'created': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
            'status': 'Active'
        }
        
        if self.todo.selected_attachment["path"] and self.todo.drive_service and self.todo.data_manager.lms_root_id:
            try:
                show_snackbar(self.todo.page, "Uploading attachment to subject folder...", ft.Colors.BLUE)
                self.todo.page.update()
                
                result = self.todo.storage_manager.upload_assignment_attachment(
                    self.todo.selected_attachment["path"],
                    self.todo.selected_attachment["name"],
                    subject,
                    new_assignment['id']
                )
                
                if result:
                    new_assignment['attachment_file_id'] = result.get('id')
                    new_assignment['attachment_file_link'] = result.get('webViewLink')
                    show_snackbar(self.todo.page, "Attachment uploaded successfully!", ft.Colors.GREEN)
                else:
                    show_snackbar(self.todo.page, "Warning: Attachment upload failed", ft.Colors.ORANGE)
            except Exception as ex:
                show_snackbar(self.todo.page, f"Attachment upload error: {str(ex)}", ft.Colors.ORANGE)
        elif self.todo.selected_attachment["path"] and not self.todo.data_manager.lms_root_id:
            show_snackbar(self.todo.page, "Warning: No LMS storage folder configured. Attachment not uploaded.", ft.Colors.ORANGE) 
        self.todo.assignments.append(new_assignment)
        self.todo.data_manager.save_assignments(self.todo.assignments)
        
        if self.todo.notification_service and self.todo.students:
            self.todo.notification_service.notify_new_assignment(new_assignment, self.todo.students)
        
        self._reset_form()
        
        self.todo.display_assignments()
        show_snackbar(self.todo.page, "Assignment added! Students notified.", ft.Colors.GREEN)
        
        if self.todo.students:
            import os
            os.environ['FIREBASE_DB_URL'] = "https://gdrive-manager-479819-default-rtdb.asia-southeast1.firebasedatabase.app"
            
            from services.fcm_service import get_fcm_service
            
            fcm = get_fcm_service()
            student_emails = [s['email'] for s in self.todo.students]
            
            fcm.send_to_multiple(
                emails=student_emails,
                title=f"New Assignment: {new_assignment['title']}",
                body=f"Subject: {new_assignment['subject']} | Due: {deadline_str}",
                data={
                    "assignment_id": new_assignment['id'],
                    "subject": new_assignment['subject']
                },
                notification_type="new_assignment"
            )
            
            show_snackbar(self.todo.page, 
                f"Assignment created and {len(student_emails)} students notified!", 
                ft.Colors.GREEN)
        
    def show_past_deadline_dialog(self, deadline, current_time):
        """Display a warning dialog if the selected deadline is in the past.

        Purpose:
            Alerts the teacher that the selected date/time is invalid for a deadline.

        Args:
            deadline (datetime): The selected deadline.
            current_time (datetime): Current system time.

        Interactions:
            - Shows `ft.AlertDialog`.
            - Updates `todo.page`.

        Algorithm:
            1. Format deadline and current time strings.
            2. Build AlertDialog with red warning icon.
            3. Display comparison of Selected vs Current time.
            4. Set `page.dialog = dialog` and open.
        """
        
        def close_dialog(e):
            dialog.open = False
            self.todo.page.update()
        
        deadline_str = deadline.strftime('%I:%M %p on %B %d, %Y')
        current_str = current_time.strftime('%I:%M %p on %B %d, %Y')
        
        dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED, size=30),
                ft.Text("Deadline is in the Past", color=ft.Colors.RED)
            ]),
            content=ft.Column([
                ft.Text("Cannot create assignment with a past deadline.", weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.SCHEDULE, size=20, color=ft.Colors.GREY_700),
                            ft.Text("Selected deadline:", weight=ft.FontWeight.BOLD)
                        ]),
                        ft.Text(deadline_str, size=15, color=ft.Colors.RED),
                        ft.Container(height=10),
                        ft.Row([
                            ft.Icon(ft.Icons.ACCESS_TIME, size=20, color=ft.Colors.GREY_700),
                            ft.Text("Current time:", weight=ft.FontWeight.BOLD)
                        ]),
                        ft.Text(current_str, size=15, color=ft.Colors.GREEN),
                    ]),
                    padding=10,
                    bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.ORANGE),
                    border_radius=5
                ),
                ft.Container(height=10),
                ft.Text("Please select a future date and time.", italic=True, color=ft.Colors.GREY_700)
            ], tight=True, spacing=10),
            actions=[
                ft.TextButton("OK", on_click=close_dialog)
            ],
        )
        
        self.todo.page.dialog = dialog
        dialog.open = True
        self.todo.page.update()
    
    def show_validation_errors(self, errors):
        """Display a dialog listing form validation errors.

        Purpose:
            Provides specific feedback on why assignment creation failed.

        Args:
            errors (list[str]): List of error messages to display.

        Interactions:
            - Shows `ft.AlertDialog`.
            - Calls `todo.show_snackbar`.

        Algorithm:
            1. Create a list of UI rows for each error message.
            2. Build AlertDialog showing all errors.
            3. Open dialog.
            4. Show summary via snackbar.
        """
        
        def close_dialog(e):
            dialog.open = False
            self.todo.page.update()
        
        error_list = ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=16, color=ft.Colors.RED),
                ft.Text(error, size=14)
            ], spacing=10)
            for error in errors
        ], spacing=8)
        
        dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.WARNING, color=ft.Colors.ORANGE, size=30),
                ft.Text("Cannot Create Assignment", color=ft.Colors.ORANGE)
            ]),
            content=ft.Column([
                ft.Text("Please fix the following errors:", weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Container(
                    content=error_list,
                    padding=10,
                    bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.RED),
                    border_radius=5
                ),
                ft.Container(height=10),
                ft.Text("Fill in all required fields and try again.", 
                       italic=True, color=ft.Colors.GREY_700, size=12)
            ], tight=True, spacing=10),
            actions=[
                ft.TextButton("OK, I'll Fix It", on_click=close_dialog)
            ],
        )
        
        self.todo.page.dialog = dialog
        dialog.open = True
        self.todo.page.update()
        
        error_count = len(errors)
        show_snackbar(self.todo.page,
            f"{error_count} error{'s' if error_count > 1 else ''} - Please fix before creating assignment",
            ft.Colors.RED
        )
    
    def _reset_form(self):
        """Clear all inputs in the 'New Assignment' form.

        Purpose:
            Resets all input fields and state variables to default values after successful creation.

        Interactions:
            - Clears `todo` input fields (title, description, score, etc.).
            - Resets `selected_attachment` and `selected_drive_folder_id`.
        """
        self.todo.assignment_title.value = ""
        self.todo.assignment_description.value = ""
        self.todo.subject_dropdown.value = None
        self.todo.max_score_field.value = ""
        self.todo.selected_deadline_display.value = "No deadline selected"
        self.todo.selected_date_value = None
        self.todo.selected_time_value = None
        self.todo.attachment_text.value = "No file attached"
        self.todo.selected_attachment["path"] = None
        self.todo.selected_attachment["name"] = None
        self.todo.selected_drive_folder_id = None
        self.todo.drive_folder_label.value = "No folder selected"
    
    def display_teacher_view(self):
        """Render the assignment list for the teacher mode.

        Purpose:
            Displays assignments with administrative controls (Edit, Delete, View Submissions).

        Interactions:
            - Reads `todo.assignments`.
            - Reads `todo.filter_dropdown`.
            - Calls `create_teacher_assignment_card`.

        Algorithm:
            1. Get current filter (All, Active, Completed, Overdue).
            2. Filter `todo.assignments` based on deadline status.
            3. If empty -> Show placeholder.
            4. Else -> Loop through assignments, create cards, append to UI column.
        """
        filtered = self.todo.assignments
        if self.todo.filter_dropdown.value != "All":
            filtered = [a for a in self.todo.assignments 
                       if self.get_status(a.get('deadline')) == self.todo.filter_dropdown.value]
        
        if not filtered:
            self.todo.assignment_column.controls.append(
                ft.Container(
                    content=ft.Text("No assignments found", size=16, color=ft.Colors.GREY),
                    padding=20,
                    alignment=ft.alignment.center
                )
            )
        else:
            for assignment in filtered:
                card = self.create_teacher_assignment_card(assignment)
                self.todo.assignment_column.controls.append(card)
    
    def display_student_view(self):
        """Render the assignment list for the student mode.

        Purpose:
            Displays relevant assignments for the logged-in student, respecting bridging/regular status.

        Interactions:
            - Reads `todo.assignments`, `todo.students`.
            - Calls `notification_service` for unread counts.
            - Calls `create_student_assignment_card`.

        Algorithm:
            1. Check notifications -> show alert if unread messages exist.
            2. Verify student selected; if not, show error.
            3. Determine student type (Bridging vs Regular).
            4. Filter assignments:
               a. Match target audience (All vs Matching Type).
               b. Apply status filter (Active, etc.).
            5. Render cards or empty state.
        """
        if self.todo.notification_service and self.todo.current_student_email:
            unread_count = self.todo.notification_service.get_unread_count(self.todo.current_student_email)
            if unread_count > 0:
                self.todo.assignment_column.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, color=ft.Colors.ORANGE),
                            ft.Text(f"You have {unread_count} new notification(s)", 
                                   size=14, color=ft.Colors.ORANGE),
                            ft.TextButton("View All", 
                                         on_click=lambda e: self.show_notifications_dialog())
                        ]),
                        padding=10,
                        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.ORANGE),
                        border_radius=8
                    )
                )
        
        if not self.todo.current_student_email:
            self.todo.assignment_column.controls.append(
                ft.Text("Please select a student from the dropdown", size=16, color=ft.Colors.RED)
            )
            return
        
        current_student = next((s for s in self.todo.students 
                               if s.get('email') == self.todo.current_student_email), None)
        is_bridging = current_student.get('is_bridging', False) if current_student else False
        
        filtered = []
        for a in self.todo.assignments:
            target = a.get('target_for', 'all')
            if target == 'all':
                filtered.append(a)
            elif target == 'bridging' and is_bridging:
                filtered.append(a)
            elif target == 'regular' and not is_bridging:
                filtered.append(a)
        
        if self.todo.filter_dropdown.value != "All":
            filtered = [a for a in filtered 
                       if self.get_status(a.get('deadline'), a['id']) == self.todo.filter_dropdown.value]
        
        if not filtered:
            self.todo.assignment_column.controls.append(
                ft.Container(
                    content=ft.Text("No assignments found", size=16, color=ft.Colors.GREY),
                    padding=20,
                    alignment=ft.alignment.center
                )
            )
        else:
            for assignment in filtered:
                card = self.create_student_assignment_card(assignment)
                self.todo.assignment_column.controls.append(card)
    
    def create_teacher_assignment_card(self, assignment):
        """Build a UI card for an assignment (Teacher View).

        Purpose:
            Generates a visual card component containing assignment details and management actions.

        Args:
            assignment (dict): Assignment data object.

        Returns:
            ft.Container: The UI card component ready for display.

        Interactions:
            - Calls `view_submissions_dialog` (via button).
            - Calls `edit_assignment_dialog` (via button).
            - Calls `delete_assignment` (via button).

        Algorithm:
            1. Calculate statistics (status, time remaining, submission count).
            2. Build status badge.
            3. Build Drive folder link (if linked).
            4. Build Attachment preview/link (if present).
            5. Build Management Buttons (View Submissions, Edit, Delete).
            6. Assemble into styled Container.
        """
        status = self.get_status(assignment.get('deadline'))
        time_remaining = self.get_time_remaining(assignment.get('deadline'))
        submission_count = self.get_submission_count(assignment['id'])
        total_students = len(self.todo.students)
        
        status_color = {
            "Active": ft.Colors.GREEN,
            "Completed": ft.Colors.BLUE,
            "Overdue": ft.Colors.RED
        }.get(status, ft.Colors.GREY)
        
        drive_folder_id = assignment.get('drive_folder_id')
        drive_folder_name = self.todo.get_folder_name_by_id(drive_folder_id) if drive_folder_id else None
        
        drive_row = ft.Row([
            ft.Icon(ft.Icons.FOLDER_SHARED, size=16, color=ft.Colors.BLUE),
            ft.Text(f"Drive: {drive_folder_name}", size=13, color=ft.Colors.BLUE),
            ft.IconButton(
                icon=ft.Icons.OPEN_IN_NEW,
                icon_size=16,
                tooltip="Open in Drive",
                on_click=lambda e, fid=drive_folder_id: self.open_drive_folder(fid)
            ) if self.todo.drive_service else ft.Container()
        ]) if drive_folder_name else ft.Container()
        
        attachment_row = ft.Container()
        if assignment.get('attachment'):
            attachment_controls = [
                ft.Icon(ft.Icons.ATTACH_FILE, size=16, color=ft.Colors.GREY_700),
                ft.Text(f"Attachment: {assignment['attachment']}", size=13, color=ft.Colors.GREY_700)
            ]
            
            if assignment.get('attachment_file_id') and self.file_preview:
                attachment_controls.append(
                    ft.IconButton(
                        icon=ft.Icons.VISIBILITY,
                        icon_size=16,
                        tooltip="Preview Attachment",
                        on_click=lambda e, fid=assignment['attachment_file_id'], 
                                fname=assignment['attachment']: self.file_preview and self.file_preview.show_preview(file_id=fid, file_name=fname)
                    )
                )
            
            if assignment.get('attachment_file_link'):
                attachment_controls.append(
                    ft.IconButton(
                        icon=ft.Icons.OPEN_IN_NEW,
                        icon_size=16,
                        tooltip="Open in Drive",
                        on_click=lambda e, link=assignment['attachment_file_link']: open_url(link)
                    )
                )
            elif assignment.get('attachment_file_id'):
                attachment_controls.append(
                    ft.IconButton(
                        icon=ft.Icons.OPEN_IN_NEW,
                        icon_size=16,
                        tooltip="Open in Drive",
                        on_click=lambda e, fid=assignment['attachment_file_id']: open_drive_file(fid)
                    )
                )
            
            attachment_row = ft.Row(attachment_controls)
        
        target_for = assignment.get('target_for', 'all')
        target_labels = {'all': 'All Students', 'bridging': 'Bridging Only', 'regular': 'Regular Only'}
        target_colors = {'all': ft.Colors.GREY_700, 'bridging': ft.Colors.ORANGE, 'regular': ft.Colors.BLUE}
        target_badge = ft.Container(
            content=ft.Text(target_labels.get(target_for, 'All'), size=11, color=ft.Colors.WHITE),
            bgcolor=target_colors.get(target_for, ft.Colors.GREY),
            padding=ft.padding.symmetric(horizontal=8, vertical=2),
            border_radius=10
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(assignment['title'], size=18, weight=ft.FontWeight.BOLD, expand=True),
                    ft.Container(
                        content=ft.Text(status, size=12, color=ft.Colors.WHITE),
                        bgcolor=status_color,
                        padding=5,
                        border_radius=5
                    ),
                ]),
                ft.Divider(height=1),
                ft.Text(f"Subject: {assignment.get('subject', 'N/A')}", size=14),
                ft.Text(assignment.get('description', 'No description'), size=14, max_lines=3),
                ft.Row([
                    ft.Icon(ft.Icons.ACCESS_TIME, size=16),
                    ft.Text(time_remaining, size=13, italic=True)
                ]),
                ft.Text(f"Max Score: {assignment.get('max_score', 'N/A')}", size=13),
                drive_row,
                attachment_row,
                ft.Row([
                    ft.Icon(ft.Icons.PEOPLE, size=16),
                    ft.Text(f"Submissions: {submission_count}/{total_students}", size=13),
                    target_badge
                ]),
                ft.Row([
                    ft.ElevatedButton(
                        "View Submissions",
                        on_click=lambda e, a=assignment: self.todo.submission_manager.view_submissions_dialog(a),
                        icon=ft.Icons.ASSIGNMENT_TURNED_IN
                    ),
                    ft.IconButton(
                        icon=ft.Icons.EDIT,
                        tooltip="Edit",
                        on_click=lambda e, a=assignment: self.edit_assignment_dialog(a)
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        tooltip="Delete",
                        icon_color=ft.Colors.RED,
                        on_click=lambda e, a=assignment: self.delete_assignment(a)
                    ),
                ], alignment=ft.MainAxisAlignment.END, spacing=0),
            ]),
            padding=10,
            border_radius=10,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLUE),
            border=ft.border.all(1, ft.Colors.BLUE_GREY_100)
        )
    
    def create_student_assignment_card(self, assignment):
        """Build a UI card for an assignment (Student View).

        Purpose:
            Generates a visual card for students to view details and submit work.

        Args:
            assignment (dict): Assignment data object.

        Returns:
            ft.Container: The UI card component.

        Interactions:
            - Checks `submissions` for current student status.
            - Calls `submission_manager.submit_assignment_dialog`.

        Algorithm:
            1. Determine status (Active/Overdue) and submission state (Submitted/Not).
            2. Build Attachment section (Download/Preview).
            3. Build Submission Status section (Grade, Feedback).
            4. Build Action Buttons:
               a. "Submit Assignment" (if active/not submitted).
               b. "Resubmit" (if submitted).
               c. "Preview Submission" (if file uploaded).
            5. Assemble into styled Container.
        """
        status = self.get_status(assignment.get('deadline'), assignment['id'])
        time_remaining = self.get_time_remaining(assignment.get('deadline'))
        submission = self.todo.submission_manager.get_submission_status(assignment['id'], self.todo.current_student_email)
        
        status_color = {
            "Active": ft.Colors.GREEN,
            "Completed": ft.Colors.BLUE,
            "Overdue": ft.Colors.RED
        }.get(status, ft.Colors.GREY)
        
        drive_folder_id = assignment.get('drive_folder_id')
        drive_folder_name = self.todo.get_folder_name_by_id(drive_folder_id) if drive_folder_id else None
        
        attachment_row = ft.Container()
        if assignment.get('attachment'):
            attachment_controls = [
                ft.Icon(ft.Icons.ATTACH_FILE, size=16, color=ft.Colors.PURPLE),
                ft.Text(f"Attachment: {assignment['attachment']}", size=13, color=ft.Colors.PURPLE, 
                       weight=ft.FontWeight.BOLD)
            ]
            
            if assignment.get('attachment_file_id') and self.file_preview:
                attachment_controls.append(
                    ft.IconButton(
                        icon=ft.Icons.VISIBILITY,
                        icon_size=18,
                        icon_color=ft.Colors.BLUE,
                        tooltip="Preview Attachment",
                        on_click=lambda e, fid=assignment['attachment_file_id'], 
                                fname=assignment['attachment']: self.file_preview and self.file_preview.show_preview(file_id=fid, file_name=fname)
                    )
                )
            
            if assignment.get('attachment_file_link'):
                attachment_controls.append(
                    ft.IconButton(
                        icon=ft.Icons.DOWNLOAD,
                        icon_size=18,
                        icon_color=ft.Colors.GREEN,
                        tooltip="Download Attachment",
                        on_click=lambda e, link=assignment['attachment_file_link']: open_url(link)
                    )
                )
            elif assignment.get('attachment_file_id'):
                attachment_controls.append(
                    ft.IconButton(
                        icon=ft.Icons.DOWNLOAD,
                        icon_size=18,
                        icon_color=ft.Colors.GREEN,
                        tooltip="Download Attachment",
                        on_click=lambda e, fid=assignment['attachment_file_id']: open_drive_file(fid)
                    )
                )
            
            attachment_row = ft.Container(
                content=ft.Row(attachment_controls),
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.PURPLE),
                padding=8,
                border_radius=5
            )
        
        upload_btn = ft.Container()
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(assignment['title'], size=18, weight=ft.FontWeight.BOLD, expand=True),
                    ft.Container(
                        content=ft.Text(status, size=12, color=ft.Colors.WHITE),
                        bgcolor=status_color,
                        padding=5,
                        border_radius=5
                    ),
                ]),
                ft.Divider(height=1),
                ft.Text(f"Subject: {assignment.get('subject', 'N/A')}", size=14),
                ft.Text(assignment.get('description', 'No description'), size=14, max_lines=3),
                ft.Row([
                    ft.Icon(ft.Icons.ACCESS_TIME, size=16),
                    ft.Text(time_remaining, size=13, italic=True)
                ]),
                ft.Text(f"Max Score: {assignment.get('max_score', 'N/A')}", size=13),
                ft.Row([
                    ft.Icon(ft.Icons.FOLDER_SHARED, size=16, color=ft.Colors.BLUE),
                    ft.Text(f"Submit to: {drive_folder_name}", size=13, color=ft.Colors.BLUE),
                ]) if drive_folder_name else ft.Container(),
                attachment_row,
                ft.Row([
                    ft.Icon(ft.Icons.ASSIGNMENT, size=16),
                    ft.Text(
                        f"Status: {'Submitted ✓' if submission else 'Not Submitted'}",
                        size=13,
                        color=ft.Colors.GREEN if submission else ft.Colors.ORANGE
                    )
                ]),
                ft.Row([
                    ft.Text(
                        f"Grade: {submission.get('grade', 'Not graded')}" if submission else "",
                        size=13,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE
                    ),
                    ft.Text(
                        f"Feedback: {submission.get('feedback', 'No feedback')}" if submission else "",
                        size=12,
                        italic=True,
                        expand=True
                    )
                ]) if submission else ft.Container(),
                ft.Row([
                    ft.ElevatedButton(
                        "Preview Submission",
                        icon=ft.Icons.VISIBILITY,
                        on_click=lambda e, s=submission: self._preview_submission_file(s)
                    ) if submission and submission.get('file_id') and self.file_preview else ft.Container(),
                    upload_btn,
                    ft.ElevatedButton(
                        "Submit Assignment" if not submission else "Resubmit",
                        on_click=lambda e, a=assignment: self.todo.submission_manager.submit_assignment_dialog(a),
                        icon=ft.Icons.UPLOAD,
                        bgcolor=ft.Colors.BLUE if not submission else ft.Colors.ORANGE
                    ) if status != "Overdue" or submission else ft.Text("Deadline passed", color=ft.Colors.RED)
                ], spacing=10)
            ], spacing=5),
            padding=15,
            border_radius=10,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLUE),
            border=ft.border.all(1, ft.Colors.BLUE_GREY_100)
        )
    
    def get_time_remaining(self, deadline_str):
        """Calculate and format the time remaining until a deadline.

        Purpose:
            Provides a human-readable countdown string (e.g., "2d 5h remaining").

        Args:
            deadline_str (str): ISO formatted deadline string.

        Returns:
            str: "Overdue", formatted time string, or error message.

        Algorithm:
            1. Parse ISO string to datetime.
            2. Compare with `now`.
            3. If past -> Return "Overdue".
            4. Calculate delta (days, hours, minutes).
            5. Return formatted string.
        """
        if not deadline_str:
            return "No deadline"
        try:
            deadline = datetime.datetime.fromisoformat(deadline_str)
            now = datetime.datetime.now()
            remaining = deadline - now
            
            if remaining.total_seconds() <= 0:
                return "Overdue"
            
            days = remaining.days
            hours = remaining.seconds // 3600
            
            if days > 0:
                return f"⏱️ {days}d {hours}h remaining"
            elif hours > 0:
                minutes = (remaining.seconds % 3600) // 60
                return f"⏱️ {hours}h {minutes}m remaining"
            else:
                minutes = remaining.seconds // 60
                return f"⏱️ {minutes}m remaining"
        except Exception as e:
            print(f"Error parsing deadline: {e}")
            return "Invalid deadline"
    
    def get_status(self, deadline_str, assignment_id=None):
        """Determine the status of an assignment.

        Purpose:
            Calculates whether an assignment is "Active", "Overdue", or "Completed".

        Args:
            deadline_str (str): ISO formatted deadline.
            assignment_id (str, optional): Assignment ID (for checking submission status).

        Returns:
            str: Status string ("Completed", "Overdue", "Active").

        Algorithm:
            1. If student mode: Check if submitted -> Return "Completed".
            2. If no deadline -> Return "Active".
            3. Compare deadline with current time.
            4. If past -> "Overdue".
            5. Else -> "Active".
        """
        if self.todo.current_mode == "student" and assignment_id and self.todo.current_student_email:
            submission = self.todo.submission_manager.get_submission_status(assignment_id, self.todo.current_student_email)
            if submission:
                return "Completed"
        
        if not deadline_str:
            return "Active"
        
        try:
            deadline = datetime.datetime.fromisoformat(deadline_str)
            now = datetime.datetime.now()
            
            if now > deadline:
                return "Overdue"
            return "Active"
        except Exception as e:
            print(f"Error parsing deadline in get_status: {e}, deadline_str: {deadline_str}")
            return "Active"
    
    
    def get_submission_count(self, assignment_id):
        """Count total submissions for an assignment.

        Purpose:
            Calculates how many students have submitted work for an assignment.

        Args:
            assignment_id (str): Assignment ID.

        Returns:
            int: Number of submissions.
        """
        return sum(1 for sub in self.todo.submissions if sub['assignment_id'] == assignment_id)
    
    def open_drive_folder(self, folder_id):
        """Open a Google Drive folder in the system's default browser.

        Purpose:
            Directs the user to the external Google Drive interface for a folder.

        Args:
            folder_id (str): Drive folder ID.

        Interactions:
            - Uses `webbrowser` module.
        """
        if self.todo.drive_service:
            import webbrowser
            url = f"https://drive.google.com/drive/folders/{folder_id}"
            webbrowser.open(url)
    
    def _preview_submission_file(self, submission):
        """Show preview for a submission file.

        Purpose:
            Opens the file preview service for a student's submitted file.

        Args:
            submission (dict): Submission record containing file_id.

        Interactions:
            - Calls `file_preview.show_preview`.
        """
        if self.file_preview and submission.get('file_id'):
            file_name = submission.get('file_name', 'Submission')
            self.file_preview.show_preview(file_id=submission['file_id'], file_name=file_name)
    
    def edit_assignment_dialog(self, assignment):
        """Open a dialog to edit an existing assignment.

        Purpose:
            Provides a form to modify assignment details (Title, Description, Score, Attachment, Folder, Audience).

        Args:
            assignment (dict): Assignment data to edit.

        Interactions:
            - Calls `storage_manager.create_browse_dialog` (Folder picker).
            - Calls `data_manager.save_assignments`.
            - Calls `storage_manager.upload_assignment_attachment` (if new file picked).

        Algorithm:
            1. Pre-fill UI fields with current data.
            2. Setup FilePicker for replacing attachment.
            3. Setup Folder Browser for changing submission folder.
            4. On Save:
               a. Update simple fields (title, desc, score).
               b. If attachment changed -> Upload new file -> Update IDs/Link.
               c. Save to DataManager.
               d. Refresh UI.
        """
        title_field = ft.TextField(value=assignment['title'], label="Title", width=320)
        desc_field = ft.TextField(
            value=assignment.get('description', ''),
            label="Description",
            multiline=True,
            min_lines=2,
            width=320
        )
        score_field = ft.TextField(value=assignment.get('max_score', '100'), label="Max Score", width=100)
        
        current_fid = [assignment.get('drive_folder_id')]
        initial_name = "None"
        if current_fid[0]:
            initial_name = self.todo.get_folder_name_by_id(current_fid[0])
        
        folder_label = ft.Text(f"Folder: {initial_name}", size=12, italic=True)
        
        current_attachment = {'path': None, 'name': assignment.get('attachment'), 
                             'file_id': assignment.get('attachment_file_id')}
        attachment_display = ft.Text(
            f"Current: {current_attachment['name']}" if current_attachment['name'] else "No attachment",
            size=12, italic=True
        )
        
        def on_file_picked(e: ft.FilePickerResultEvent):
            if e.files:
                current_attachment['path'] = e.files[0].path
                current_attachment['name'] = e.files[0].name
                attachment_display.value = f"New: {e.files[0].name}"
                self.todo.page.update()
        
        file_picker = ft.FilePicker(on_result=on_file_picked)
        self.todo.page.overlay.append(file_picker)
        self.todo.page.update()
        
        change_attachment_btn = ft.TextButton(
            "Change Attachment",
            icon=ft.Icons.ATTACH_FILE,
            on_click=lambda e: file_picker.pick_files()
        )
        
        def update_edit_folder(fid):
            current_fid[0] = fid
            name = self.todo.get_folder_name_by_id(fid)
            folder_label.value = f"Selected: {name}"
            self.todo.page.update()
        
        change_folder_btn = ft.TextButton(
            "Change Folder",
            icon=ft.Icons.FOLDER_OPEN,
            on_click=lambda e: self.todo.storage_manager.create_browse_dialog(
                current_fid[0] or self.todo.data_manager.lms_root_id or 'root',
                update_edit_folder
            )
        )
        
        target_dropdown = ft.Dropdown(
            label="Assign To",
            value=assignment.get('target_for', 'all'),
            options=[
                ft.dropdown.Option("all", "All Students"),
                ft.dropdown.Option("bridging", "Bridging Only"),
                ft.dropdown.Option("regular", "Regular Only"),
            ],
            width=150
        )
        
        def save(e):
            assignment['title'] = title_field.value
            assignment['description'] = desc_field.value
            assignment['max_score'] = score_field.value
            assignment['drive_folder_id'] = current_fid[0]
            assignment['target_for'] = target_dropdown.value
            
            if current_attachment['path'] and self.todo.drive_service and self.todo.data_manager.lms_root_id:
                try:
                    show_snackbar(self.todo.page, "Uploading new attachment...", ft.Colors.BLUE)
                    self.todo.page.update()
                    
                    result = self.todo.storage_manager.upload_assignment_attachment(
                        current_attachment['path'],
                        current_attachment['name'],
                        assignment['subject'],
                        assignment['id']
                    )
                    
                    if result:
                        assignment['attachment'] = current_attachment['name']
                        assignment['attachment_file_id'] = result.get('id')
                        assignment['attachment_file_link'] = result.get('webViewLink')
                        show_snackbar(self.todo.page, "Attachment uploaded!", ft.Colors.GREEN)
                except Exception as ex:
                    show_snackbar(self.todo.page, f"Attachment upload error: {str(ex)}", ft.Colors.ORANGE)
            
            self.todo.data_manager.save_assignments(self.todo.assignments)
            close_overlay(e)
            self.todo.display_assignments()
            show_snackbar(self.todo.page, "Assignment updated", ft.Colors.BLUE)
        
        content = ft.Column([
            title_field,
            desc_field,
            ft.Row([score_field, target_dropdown], spacing=10),
            ft.Row([folder_label, change_folder_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            ft.Text("Attachment:", weight=ft.FontWeight.BOLD, size=13),
            ft.Row([attachment_display, change_attachment_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=10),
            ft.Row([
                ft.TextButton("Cancel", on_click=lambda e: close_overlay(e)),
                ft.ElevatedButton("Save", on_click=save, icon=ft.Icons.SAVE)
            ], alignment=ft.MainAxisAlignment.END)
        ], spacing=10)
        
        overlay, close_overlay = self.todo.show_overlay(content, "Edit Assignment", width=400)
    
    def delete_assignment(self, assignment):
        """Show confirmation dialog to delete an assignment.

        Purpose:
            Permanently removes an assignment and all its associated submissions.

        Args:
            assignment (dict): Assignment to delete.

        Interactions:
            - Modifies `todo.assignments`, `todo.submissions`.
            - Calls `data_manager.save_assignments`, `save_submissions`.

        Algorithm:
            1. Show confirmation dialog.
            2. On Confirm:
               a. Filter out assignment from list.
               b. Filter out linked submissions from list.
               c. Save updated lists.
               d. Refresh display and show snackbar.
        """
        def confirm(e):
            self.todo.assignments = [a for a in self.todo.assignments if a['id'] != assignment['id']]
            self.todo.submissions = [s for s in self.todo.submissions 
                                     if s['assignment_id'] != assignment['id']]
            self.todo.data_manager.save_assignments(self.todo.assignments)
            self.todo.data_manager.save_submissions(self.todo.submissions)
            close_overlay(e)
            self.todo.display_assignments()
            show_snackbar(self.todo.page,"Assignment deleted", ft.Colors.ORANGE)
        
        content = ft.Column([
            ft.Text(f"Delete '{assignment['title']}'?"),
            ft.Text("This will also delete all submissions.", size=12, color=ft.Colors.GREY_600),
            ft.Container(height=10),
            ft.Row([ 
                ft.TextButton("Cancel", on_click=lambda e: close_overlay(e)),
                ft.ElevatedButton("Delete", on_click=confirm, bgcolor=ft.Colors.RED, color=ft.Colors.WHITE)
            ], alignment=ft.MainAxisAlignment.END)
        ], tight=True, spacing=10)
        
        overlay, close_overlay = self.todo.show_overlay(content, "Confirm Delete", width=350)
    
    def show_notifications_dialog(self):
        """Show a dialog listing recent notifications for the current student.

        Purpose:
            Displays a scrollable list of alerts/messages and allows marking them as read.

        Interactions:
            - Calls `notification_service.get_notifications_for_student`.
            - Calls `notification_service.mark_as_read`.

        Algorithm:
            1. Fetch notifications for current email.
            2. Render list:
               a. Highlight unread items.
               b. Click to mark read.
            3. Provide "Mark All Read" button.
            4. Show in Overlay.
        """
        if not self.todo.notification_service:
            return
        
        notifications = self.todo.notification_service.get_notifications_for_student(
            self.todo.current_student_email
        )
        notifications_list = ft.Column(scroll="auto", spacing=5)
        
        if not notifications:
            notifications_list.controls.append(ft.Text("No notifications", color=ft.Colors.GREY))
        else:
            for n in reversed(notifications[-20:]):
                is_unread = not n.get('read', False)
                notifications_list.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.CIRCLE, size=8,
                                       color=ft.Colors.BLUE if is_unread else ft.Colors.GREY),
                                ft.Text(n.get('title', 'Notification'),
                                       weight=ft.FontWeight.BOLD if is_unread else ft.FontWeight.NORMAL),
                            ]),
                            ft.Text(n.get('message', ''), size=12),
                            ft.Text(n.get('created_at', ''), size=10, color=ft.Colors.GREY),
                        ]),
                        padding=8,
                        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLUE) if is_unread else None,
                        border_radius=5,
                        on_click=lambda e, nid=n['id']: self.todo.notification_service.mark_as_read(nid)
                    )
                )
        
        def mark_all_read(e):
            self.todo.notification_service.mark_all_as_read(self.todo.current_student_email)
            show_snackbar(self.todo.page, "All notifications marked as read", ft.Colors.BLUE)
            close_overlay(e)
            self.todo.display_assignments()
        
        content = ft.Column([
            ft.Container(content=notifications_list, width=400, height=300),
            ft.Row([
                ft.TextButton("Mark All Read", on_click=mark_all_read),
                ft.TextButton("Close", on_click=lambda e: close_overlay(e))
            ], alignment=ft.MainAxisAlignment.END)
        ])
        
        overlay, close_overlay = self.todo.show_overlay(content, "Notifications", width=450)