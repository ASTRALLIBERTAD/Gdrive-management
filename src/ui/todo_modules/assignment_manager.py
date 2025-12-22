import flet as ft
import datetime
from utils.validators import Validator, DateTimeUtils
from utils.ui_components import DialogManager
from utils.common import open_drive_folder, open_drive_file, open_url


class AssignmentManager:
    
    def __init__(self, todo_view):
        self.todo = todo_view
        self.dialog_mgr = DialogManager(todo_view.page)
        
        try:
            from services.file_preview_service import FilePreviewService
            self.file_preview = FilePreviewService(todo_view.page, todo_view.drive_service)
        except ImportError:
            self.file_preview = None
    
    def add_assignment(self, e):
        title = self.todo.assignment_title.value.strip() if self.todo.assignment_title.value else ""
        description = self.todo.assignment_description.value.strip() if self.todo.assignment_description.value else ""
        subject = self.todo.subject_dropdown.value
        max_score = self.todo.max_score_field.value.strip() if self.todo.max_score_field.value else ""
        drive_folder_id = self.todo.selected_drive_folder_id
        target_for = self.todo.target_dropdown.value or "all"
        
        errors = Validator.validate_required_fields({
            "Assignment title": title,
            "Subject": subject
        })
        
        if errors:
            for field, error in [("assignment_title", "Title"), ("subject_dropdown", "Subject")]:
                widget = getattr(self.todo, field)
                if error in str(errors):
                    widget.error_text = "Required"
                    widget.border_color = ft.Colors.RED
                else:
                    widget.error_text = None
                    widget.border_color = None
        
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
            if Validator.is_past_datetime(final_deadline):
                time_ago = DateTimeUtils.time_since(final_deadline)
                errors.append(f"⏰ Deadline is in the past ({time_ago})")
                self.todo.selected_deadline_display.value = f"Invalid: {time_ago}"
                self.todo.selected_deadline_display.color = ft.Colors.RED
            else:
                deadline_str = DateTimeUtils.format_datetime(final_deadline, '%B %d, %Y at %I:%M %p')
                self.todo.selected_deadline_display.value = f"✓ Deadline: {deadline_str}"
                self.todo.selected_deadline_display.color = ft.Colors.GREEN
        else:
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
                self.dialog_mgr.show_snackbar("Uploading attachment to subject folder...", ft.Colors.BLUE)
                
                result = self.todo.storage_manager.upload_assignment_attachment(
                    self.todo.selected_attachment["path"],
                    self.todo.selected_attachment["name"],
                    subject,
                    new_assignment['id']
                )
                
                if result:
                    new_assignment['attachment_file_id'] = result.get('id')
                    new_assignment['attachment_file_link'] = result.get('webViewLink')
                    self.dialog_mgr.show_snackbar("Attachment uploaded successfully!", ft.Colors.GREEN)
                else:
                    self.dialog_mgr.show_snackbar("Warning: Attachment upload failed", ft.Colors.ORANGE)
            except Exception as ex:
                self.dialog_mgr.show_snackbar(f"Attachment upload error: {str(ex)}", ft.Colors.ORANGE)
        elif self.todo.selected_attachment["path"] and not self.todo.data_manager.lms_root_id:
            self.dialog_mgr.show_snackbar("Warning: No LMS storage folder configured. Attachment not uploaded.", ft.Colors.ORANGE)
        
        self.todo.assignments.append(new_assignment)
        self.todo.data_manager.save_assignments(self.todo.assignments)
        
        if self.todo.notification_service and self.todo.students:
            self.todo.notification_service.notify_new_assignment(new_assignment, self.todo.students)
        
        self._reset_form()
        
        self.todo.display_assignments()
        self.dialog_mgr.show_snackbar("Assignment added! Students notified.", ft.Colors.GREEN)
    
    def show_validation_errors(self, errors):
        error_list = ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=16, color=ft.Colors.RED),
                ft.Text(error, size=14)
            ], spacing=10)
            for error in errors
        ], spacing=8)
        
        content = ft.Column([
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
        ], tight=True, spacing=10)
        
        self.dialog_mgr.show_overlay(content, "Cannot Create Assignment", width=400)
        
        error_count = len(errors)
        self.dialog_mgr.show_snackbar(
            f"{error_count} error{'s' if error_count > 1 else ''} - Please fix before creating assignment",
            ft.Colors.RED
        )
    
    def _reset_form(self):
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
        from utils.ui_components import CardBuilder
        
        status = self.get_status(assignment.get('deadline'))
        time_remaining = DateTimeUtils.time_until(assignment.get('deadline')) if assignment.get('deadline') else "No deadline"
        submission_count = self.get_submission_count(assignment['id'])
        total_students = len(self.todo.students)
        
        status_badge = CardBuilder.create_status_badge(
            status,
            {
                "Active": ft.Colors.GREEN,
                "Completed": ft.Colors.BLUE,
                "Overdue": ft.Colors.RED
            }.get(status, ft.Colors.GREY)
        )
        
        drive_folder_id = assignment.get('drive_folder_id')
        drive_folder_name = self.todo.get_folder_name_by_id(drive_folder_id) if drive_folder_id else None
        
        drive_row = CardBuilder.create_icon_text_row(
            ft.Icons.FOLDER_SHARED,
            f"Drive: {drive_folder_name}",
            ft.Colors.BLUE
        ) if drive_folder_name else ft.Container()
        
        attachment_row = self._create_attachment_row(assignment, is_teacher=True)
        
        target_for = assignment.get('target_for', 'all')
        target_labels = {'all': 'All Students', 'bridging': 'Bridging Only', 'regular': 'Regular Only'}
        target_colors = {'all': ft.Colors.GREY_700, 'bridging': ft.Colors.ORANGE, 'regular': ft.Colors.BLUE}
        target_badge = ft.Container(
            content=ft.Text(target_labels.get(target_for, 'All'), size=11, color=ft.Colors.WHITE),
            bgcolor=target_colors.get(target_for, ft.Colors.GREY),
            padding=ft.padding.symmetric(horizontal=8, vertical=2),
            border_radius=10
        )
        
        content = ft.Column([
            ft.Row([
                ft.Text(assignment['title'], size=18, weight=ft.FontWeight.BOLD, expand=True),
                status_badge,
            ]),
            ft.Divider(height=1),
            ft.Text(f"Subject: {assignment.get('subject', 'N/A')}", size=14),
            ft.Text(assignment.get('description', 'No description'), size=14, max_lines=3),
            CardBuilder.create_icon_text_row(ft.Icons.ACCESS_TIME, time_remaining, text_size=13),
            ft.Text(f"Max Score: {assignment.get('max_score', 'N/A')}", size=13),
            drive_row,
            attachment_row,
            CardBuilder.create_icon_text_row(
                ft.Icons.PEOPLE, 
                f"Submissions: {submission_count}/{total_students}"
            ),
            target_badge,
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
        ])
        
        return CardBuilder.create_container(
            content,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLUE),
            border_color=ft.Colors.BLUE_GREY_100
        )
    
    def create_student_assignment_card(self, assignment):
        from utils.ui_components import CardBuilder
        
        status = self.get_status(assignment.get('deadline'), assignment['id'])
        time_remaining = DateTimeUtils.time_until(assignment.get('deadline')) if assignment.get('deadline') else "No deadline"
        submission = self.get_submission_status(assignment['id'], self.todo.current_student_email)
        
        status_badge = CardBuilder.create_status_badge(
            status,
            {
                "Active": ft.Colors.GREEN,
                "Completed": ft.Colors.BLUE,
                "Overdue": ft.Colors.RED
            }.get(status, ft.Colors.GREY)
        )
        
        drive_folder_id = assignment.get('drive_folder_id')
        drive_folder_name = self.todo.get_folder_name_by_id(drive_folder_id) if drive_folder_id else None
        
        attachment_row = self._create_attachment_row(assignment, is_teacher=False)
        
        content = ft.Column([
            ft.Row([
                ft.Text(assignment['title'], size=18, weight=ft.FontWeight.BOLD, expand=True),
                status_badge,
            ]),
            ft.Divider(height=1),
            ft.Text(f"Subject: {assignment.get('subject', 'N/A')}", size=14),
            ft.Text(assignment.get('description', 'No description'), size=14, max_lines=3),
            CardBuilder.create_icon_text_row(ft.Icons.ACCESS_TIME, time_remaining, text_size=13),
            ft.Text(f"Max Score: {assignment.get('max_score', 'N/A')}", size=13),
            CardBuilder.create_icon_text_row(
                ft.Icons.FOLDER_SHARED,
                f"Submit to: {drive_folder_name}",
                ft.Colors.BLUE
            ) if drive_folder_name else ft.Container(),
            attachment_row,
            CardBuilder.create_icon_text_row(
                ft.Icons.ASSIGNMENT,
                f"Status: {'Submitted ✓' if submission else 'Not Submitted'}",
                None,
                13
            ),
            self._create_submission_feedback_row(submission) if submission else ft.Container(),
            ft.Row([
                ft.ElevatedButton(
                    "Preview Submission",
                    icon=ft.Icons.VISIBILITY,
                    on_click=lambda e, s=submission: self._preview_submission_file(s)
                ) if submission and submission.get('file_id') and self.file_preview else ft.Container(),
                ft.ElevatedButton(
                    "Submit Assignment" if not submission else "Resubmit",
                    on_click=lambda e, a=assignment: self.todo.submission_manager.submit_assignment_dialog(a),
                    icon=ft.Icons.UPLOAD,
                    bgcolor=ft.Colors.BLUE if not submission else ft.Colors.ORANGE
                ) if status != "Overdue" or submission else ft.Text("Deadline passed", color=ft.Colors.RED)
            ], spacing=10)
        ], spacing=5)
        
        return CardBuilder.create_container(
            content,
            padding=15,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLUE),
            border_color=ft.Colors.BLUE_GREY_100
        )
    
    def _create_attachment_row(self, assignment, is_teacher):
        if not assignment.get('attachment'):
            return ft.Container()
        
        attachment_controls = [
            ft.Icon(ft.Icons.ATTACH_FILE, size=16, color=ft.Colors.GREY_700 if is_teacher else ft.Colors.PURPLE),
            ft.Text(
                f"Attachment: {assignment['attachment']}", 
                size=13, 
                color=ft.Colors.GREY_700 if is_teacher else ft.Colors.PURPLE,
                weight=ft.FontWeight.NORMAL if is_teacher else ft.FontWeight.BOLD
            )
        ]
        
        if assignment.get('attachment_file_id') and self.file_preview:
            attachment_controls.append(
                ft.IconButton(
                    icon=ft.Icons.VISIBILITY,
                    icon_size=16 if is_teacher else 18,
                    icon_color=ft.Colors.BLUE if not is_teacher else None,
                    tooltip="Preview Attachment",
                    on_click=lambda e, fid=assignment['attachment_file_id'], 
                            fname=assignment['attachment']: self._preview_attachment(fid, fname)
                )
            )
        
        if assignment.get('attachment_file_link'):
            attachment_controls.append(
                ft.IconButton(
                    icon=ft.Icons.OPEN_IN_NEW if is_teacher else ft.Icons.DOWNLOAD,
                    icon_size=16 if is_teacher else 18,
                    icon_color=ft.Colors.GREEN if not is_teacher else None,
                    tooltip="Open in Drive" if is_teacher else "Download Attachment",
                    on_click=lambda e, link=assignment['attachment_file_link']: self._open_link(link)
                )
            )
        elif assignment.get('attachment_file_id'):
            attachment_controls.append(
                ft.IconButton(
                    icon=ft.Icons.OPEN_IN_NEW if is_teacher else ft.Icons.DOWNLOAD,
                    icon_size=16 if is_teacher else 18,
                    icon_color=ft.Colors.GREEN if not is_teacher else None,
                    tooltip="Open in Drive" if is_teacher else "Download Attachment",
                    on_click=lambda e, fid=assignment['attachment_file_id']: self._open_drive_file(fid)
                )
            )
        
        row = ft.Row(attachment_controls)
        
        if not is_teacher:
            return ft.Container(
                content=row,
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.PURPLE),
                padding=8,
                border_radius=5
            )
        
        return row
    
    def _create_submission_feedback_row(self, submission):
        return ft.Row([
            ft.Text(
                f"Grade: {submission.get('grade', 'Not graded')}",
                size=13,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLUE
            ),
            ft.Text(
                f"Feedback: {submission.get('feedback', 'No feedback')}",
                size=12,
                italic=True,
                expand=True
            )
        ])
    
    def get_time_remaining(self, deadline_str):
        return DateTimeUtils.time_until(deadline_str) if deadline_str else "No deadline"
    
    def get_status(self, deadline_str, assignment_id=None):
        if self.todo.current_mode == "student" and assignment_id and self.todo.current_student_email:
            submission = self.get_submission_status(assignment_id, self.todo.current_student_email)
            if submission:
                return "Completed"
        
        if not deadline_str:
            return "Active"
        
        return "Overdue" if Validator.is_past_datetime(deadline_str) else "Active"
    
    def get_submission_status(self, assignment_id, student_email):
        for sub in self.todo.submissions:
            if sub['assignment_id'] == assignment_id and sub['student_email'] == student_email:
                return sub
        return None
    
    def get_submission_count(self, assignment_id):
        return sum(1 for sub in self.todo.submissions if sub['assignment_id'] == assignment_id)
    
    def open_drive_folder(self, folder_id):
        if self.todo.drive_service:
            open_drive_folder(folder_id)
    
    def _preview_submission_file(self, submission):
        if self.file_preview and submission.get('file_id'):
            file_name = submission.get('file_name', 'Submission')
            self.file_preview.show_preview(file_id=submission['file_id'], file_name=file_name)
    
    def _preview_attachment(self, file_id, file_name):
        if self.file_preview:
            self.file_preview.show_preview(file_id=file_id, file_name=file_name)
    
    def _open_link(self, link):
        open_url(link)
    
    def _open_drive_file(self, file_id):
        open_drive_file(file_id)
    
    def edit_assignment_dialog(self, assignment):
        from utils.ui_components import FormField
        
        title_field = FormField.create_text_field(value=assignment['title'], label="Title", width=320)
        desc_field = FormField.create_text_field(
            value=assignment.get('description', ''),
            label="Description",
            multiline=True,
            width=320
        )
        score_field = FormField.create_text_field(
            value=assignment.get('max_score', '100'), 
            label="Max Score", 
            width=100
        )
        
        current_fid = [assignment.get('drive_folder_id')]
        initial_name = "None"
        if current_fid[0]:
            initial_name = self.todo.get_folder_name_by_id(current_fid[0])
        
        folder_label = ft.Text(f"Folder: {initial_name}", size=12, italic=True)
        
        current_attachment = {
            'path': None, 
            'name': assignment.get('attachment'), 
            'file_id': assignment.get('attachment_file_id')
        }
        attachment_display = ft.Text(
            f"Current: {current_attachment['name']}" if current_attachment['name'] else "No attachment",
            size=12, italic=True
        )
        
        file_picker = FormField.create_file_picker(
            self.todo.page,
            lambda e: self._handle_file_picked(e, current_attachment, attachment_display)
        )
        
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
        
        target_dropdown = FormField.create_dropdown(
            label="Assign To",
            options=[
                ft.dropdown.Option("all", "All Students"),
                ft.dropdown.Option("bridging", "Bridging Only"),
                ft.dropdown.Option("regular", "Regular Only"),
            ],
            width=150
        )
        target_dropdown.value = assignment.get('target_for', 'all')
        
        def save(e):
            assignment['title'] = title_field.value
            assignment['description'] = desc_field.value
            assignment['max_score'] = score_field.value
            assignment['drive_folder_id'] = current_fid[0]
            assignment['target_for'] = target_dropdown.value
            
            if current_attachment['path'] and self.todo.drive_service and self.todo.data_manager.lms_root_id:
                try:
                    self.dialog_mgr.show_snackbar("Uploading new attachment...", ft.Colors.BLUE)
                    
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
                        self.dialog_mgr.show_snackbar("Attachment uploaded!", ft.Colors.GREEN)
                except Exception as ex:
                    self.dialog_mgr.show_snackbar(f"Attachment upload error: {str(ex)}", ft.Colors.ORANGE)
            
            self.todo.data_manager.save_assignments(self.todo.assignments)
            close_overlay(e)
            self.todo.display_assignments()
            self.dialog_mgr.show_snackbar("Assignment updated", ft.Colors.BLUE)
        
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
        
        overlay, close_overlay = self.dialog_mgr.show_overlay(content, "Edit Assignment", width=400)
    
    def _handle_file_picked(self, e, attachment_dict, display_widget):
        if e.files:
            attachment_dict['path'] = e.files[0].path
            attachment_dict['name'] = e.files[0].name
            display_widget.value = f"New: {e.files[0].name}"
            self.todo.page.update()
    
    def delete_assignment(self, assignment):
        def confirm():
            self.todo.assignments = [a for a in self.todo.assignments if a['id'] != assignment['id']]
            self.todo.submissions = [s for s in self.todo.submissions 
                                     if s['assignment_id'] != assignment['id']]
            self.todo.data_manager.save_assignments(self.todo.assignments)
            self.todo.data_manager.save_submissions(self.todo.submissions)
            self.todo.display_assignments()
            self.dialog_mgr.show_snackbar("Assignment deleted", ft.Colors.ORANGE)
        
        self.dialog_mgr.show_confirmation(
            "Confirm Delete",
            f"Delete '{assignment['title']}'?\nThis will also delete all submissions.",
            confirm,
            "Delete",
            "Cancel",
            ft.Colors.RED
        )
    
    def show_notifications_dialog(self):
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
            self.dialog_mgr.show_snackbar("All notifications marked as read", ft.Colors.BLUE)
            close_overlay(e)
            self.todo.display_assignments()
        
        content = ft.Column([
            ft.Container(content=notifications_list, width=400, height=300),
            ft.Row([
                ft.TextButton("Mark All Read", on_click=mark_all_read),
                ft.TextButton("Close", on_click=lambda e: close_overlay(e))
            ], alignment=ft.MainAxisAlignment.END)
        ])
        
        overlay, close_overlay = self.dialog_mgr.show_overlay(content, "Notifications", width=450)