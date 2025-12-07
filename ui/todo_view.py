import flet as ft
import datetime
import json
import os
from pathlib import Path

SAVED_LINKS_FILE = "saved_links.json"


class TodoView:
 
    def __init__(self, page: ft.Page, on_back=None, drive_service=None):
        self.page = page
        self.on_back = on_back
        self.drive_service = drive_service
        
        self.data_dir = Path("lms_data")
        self.data_dir.mkdir(exist_ok=True)
        self.assignments_file = self.data_dir / "assignments.json"
        self.students_file = self.data_dir / "students.json"
        self.submissions_file = self.data_dir / "submissions.json"
        
        
        try:
            from services.notification_service import NotificationService
            self.notification_service = NotificationService(self.data_dir)
        except ImportError:
            self.notification_service = None
        
        self.assignments = self.load_json(self.assignments_file, [])
        self.students = self.load_json(self.students_file, [])
        self.submissions = self.load_json(self.submissions_file, [])
        
        
        self.saved_links = self.load_saved_links()
        
        for assignment in self.assignments:
            if 'id' not in assignment:
                assignment['id'] = str(datetime.datetime.now().timestamp()) + str(self.assignments.index(assignment))
        if self.assignments:
            self.save_json(self.assignments_file, self.assignments)
        
        self.current_mode = "teacher"  
        self.current_student_email = None
        
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
        
        
        self.drive_folder_dropdown = ft.Dropdown(
            hint_text="Link to Drive Folder",
            width=250,
            options=self._get_drive_folder_options()
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
        
        self.student_dropdown = ft.Dropdown(
            hint_text="Select Student",
            width=250,
            on_change=self.on_student_selected
        )
        self.update_student_dropdown()
        
        self.student_selector_row = ft.Row([
            ft.Text("Viewing as:", size=14),
            self.student_dropdown
        ], visible=False)
        
        
        self.form_container = None
        self.manage_students_btn = None

    def load_saved_links(self):
        if os.path.exists(SAVED_LINKS_FILE):
            try:
                with open(SAVED_LINKS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("links", [])
            except:
                pass
        return []
    
    def _get_bridging_students(self):
        
        return [s for s in self.students if s.get('is_bridging', False)]
    
    def _get_regular_students(self):
        
        return [s for s in self.students if not s.get('is_bridging', False)]
    
    def _refresh_students(self):
        
        self.students = self.load_json(self.students_file, [])
    
    def _validate_email(self, email):
        
        import re
        
        if not email:
            return False, "Email is required"
        
        pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Invalid email format"
        
        
        if '@gmail.com' in email.lower():
            
            local_part = email.split('@')[0]
            if len(local_part) < 6:
                return False, "Gmail addresses must have at least 6 characters before @"
        
        return True, None
    
    def _get_drive_folder_options(self):
        options = [ft.dropdown.Option("none", "No Drive folder")]
        for link in self.saved_links:
            if link.get("mimeType") == "application/vnd.google-apps.folder":
                options.append(ft.dropdown.Option(link["id"], link["name"]))
        return options
    
    def get_folder_name_by_id(self, folder_id):
        for link in self.saved_links:
            if link.get("id") == folder_id:
                return link.get("name", folder_id)
        return None

    def load_json(self, filepath, default=None):
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return default if default is not None else []

    def save_json(self, filepath, data):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)

    def on_date_selected(self, e):
        self.selected_date_value = self.date_picker.value
        self.update_deadline_display()
        self.page.close(self.date_picker)
        self.page.open(self.time_picker)
        self.page.update()

    def on_time_selected(self, e):
        self.selected_time_value = self.time_picker.value
        self.update_deadline_display()
        self.page.update()

    def update_deadline_display(self):
        if self.selected_date_value and self.selected_time_value:
            self.selected_deadline_display.value = f"Deadline: {self.selected_date_value} at {self.selected_time_value}"
        elif self.selected_date_value:
            self.selected_deadline_display.value = f"Deadline: {self.selected_date_value}"
        else:
            self.selected_deadline_display.value = "No deadline selected"

    def pick_file(self, e):
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

    def get_status(self, deadline_str):
        if not deadline_str:
            return "Active"
        try:
            deadline = datetime.datetime.fromisoformat(deadline_str)
            now = datetime.datetime.now()
            if now > deadline:
                return "Overdue"
            return "Active"
        except:
            return "Active"

    def get_time_remaining(self, deadline_str):
        if not deadline_str:
            return "No deadline"
        try:
            deadline = datetime.datetime.fromisoformat(deadline_str)
            now = datetime.datetime.now()
            remaining = deadline - now
            
            if remaining.total_seconds() <= 0:
                return "⚠️ Overdue"
            
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
        except:
            return "Invalid deadline"

    def get_submission_status(self, assignment_id, student_email):
        for sub in self.submissions:
            if sub['assignment_id'] == assignment_id and sub['student_email'] == student_email:
                return sub
        return None

    def get_submission_count(self, assignment_id):
        return sum(1 for sub in self.submissions if sub['assignment_id'] == assignment_id)

    def display_assignments(self):
        self.assignment_column.controls.clear()
        
        if self.current_mode == "teacher":
            self.display_teacher_view()
        else:
            self.display_student_view()
        
        self.page.update()

    def display_teacher_view(self):
        filtered = self.assignments
        if self.filter_dropdown.value != "All":
            filtered = [a for a in self.assignments if self.get_status(a.get('deadline')) == self.filter_dropdown.value]
        
        if not filtered:
            self.assignment_column.controls.append(
                ft.Container(
                    content=ft.Text("No assignments found", size=16, color=ft.Colors.GREY),
                    padding=20,
                    alignment=ft.alignment.center
                )
            )
        else:
            for assignment in filtered:
                card = self.create_teacher_assignment_card(assignment)
                self.assignment_column.controls.append(card)

    def display_student_view(self):
        
        if self.notification_service and self.current_student_email:
            unread_count = self.notification_service.get_unread_count(self.current_student_email)
            if unread_count > 0:
                self.assignment_column.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, color=ft.Colors.ORANGE),
                            ft.Text(f"You have {unread_count} new notification(s)", 
                                   size=14, color=ft.Colors.ORANGE),
                            ft.TextButton("View All", on_click=lambda e: self.show_notifications_dialog())
                        ]),
                        padding=10,
                        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.ORANGE),
                        border_radius=8
                    )
                )
        
        if not self.current_student_email:
            self.assignment_column.controls.append(
                ft.Text("Please select a student from the dropdown", size=16, color=ft.Colors.RED)
            )
            return
        
        
        current_student = next((s for s in self.students if s.get('email') == self.current_student_email), None)
        is_bridging = current_student.get('is_bridging', False) if current_student else False
        
        
        filtered = []
        for a in self.assignments:
            target = a.get('target_for', 'all')
            if target == 'all':
                filtered.append(a)
            elif target == 'bridging' and is_bridging:
                filtered.append(a)
            elif target == 'regular' and not is_bridging:
                filtered.append(a)
        
        
        if self.filter_dropdown.value != "All":
            filtered = [a for a in filtered if self.get_status(a.get('deadline')) == self.filter_dropdown.value]
        
        if not filtered:
            self.assignment_column.controls.append(
                ft.Container(
                    content=ft.Text("No assignments found", size=16, color=ft.Colors.GREY),
                    padding=20,
                    alignment=ft.alignment.center
                )
            )
        else:
            for assignment in filtered:
                card = self.create_student_assignment_card(assignment)
                self.assignment_column.controls.append(card)

    def create_teacher_assignment_card(self, assignment):
        status = self.get_status(assignment.get('deadline'))
        time_remaining = self.get_time_remaining(assignment.get('deadline'))
        submission_count = self.get_submission_count(assignment['id'])
        total_students = len(self.students)
        
        status_color = {
            "Active": ft.Colors.GREEN,
            "Completed": ft.Colors.BLUE,
            "Overdue": ft.Colors.RED
        }.get(status, ft.Colors.GREY)
        
        drive_folder_id = assignment.get('drive_folder_id')
        drive_folder_name = self.get_folder_name_by_id(drive_folder_id) if drive_folder_id else None
        
        drive_row = ft.Row([
            ft.Icon(ft.Icons.FOLDER_SHARED, size=16, color=ft.Colors.BLUE),
            ft.Text(f"Drive: {drive_folder_name}", size=13, color=ft.Colors.BLUE),
            ft.IconButton(
                icon=ft.Icons.OPEN_IN_NEW,
                icon_size=16,
                tooltip="Open in Drive",
                on_click=lambda e, fid=drive_folder_id: self.open_drive_folder(fid)
            ) if self.drive_service else ft.Container()
        ]) if drive_folder_name else ft.Container()
        
        
        target_for = assignment.get('target_for', 'all')
        target_labels = {'all': '👥 All Students', 'bridging': '🔄 Bridging Only', 'regular': '📚 Regular Only'}
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
                    ft.Text(
                        assignment['title'],
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        expand=True
                    ),
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
                ft.Row([
                    ft.Icon(ft.Icons.PEOPLE, size=16),
                    ft.Text(f"Submissions: {submission_count}/{total_students}", size=13),
                    target_badge
                ]),
                ft.Row([
                    ft.ElevatedButton(
                        "View Submissions",
                        on_click=lambda e, a=assignment: self.view_submissions_dialog(a),
                        icon=ft.Icons.ASSIGNMENT_TURNED_IN
                    ),
                    ft.IconButton(
                        icon=ft.Icons.EDIT,
                        tooltip="Edit",
                        on_click=lambda e, a=assignment: self.edit_assignment_dialog(a)
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_color=ft.Colors.RED,
                        tooltip="Delete",
                        on_click=lambda e, a=assignment: self.delete_assignment(a)
                    )
                ], alignment=ft.MainAxisAlignment.END)
            ], spacing=5),
            padding=15,
            border_radius=10,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLUE),
            border=ft.border.all(1, ft.Colors.BLUE_GREY_100)
        )

    def create_student_assignment_card(self, assignment):
        status = self.get_status(assignment.get('deadline'))
        time_remaining = self.get_time_remaining(assignment.get('deadline'))
        submission = self.get_submission_status(assignment['id'], self.current_student_email)
        
        status_color = {
            "Active": ft.Colors.GREEN,
            "Completed": ft.Colors.BLUE,
            "Overdue": ft.Colors.RED
        }.get(status, ft.Colors.GREY)
        
        
        drive_folder_id = assignment.get('drive_folder_id')
        drive_folder_name = self.get_folder_name_by_id(drive_folder_id) if drive_folder_id else None
        
        
        upload_btn = ft.Container()
        if drive_folder_id and drive_folder_name and self.drive_service:
            upload_btn = ft.ElevatedButton(
                "📤 Upload to Drive",
                on_click=lambda e, a=assignment: self.upload_to_drive_dialog(a),
                icon=ft.Icons.CLOUD_UPLOAD,
                bgcolor=ft.Colors.GREEN
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(
                        assignment['title'],
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        expand=True
                    ),
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
                    upload_btn,
                    ft.ElevatedButton(
                        "Submit Assignment" if not submission else "Resubmit",
                        on_click=lambda e, a=assignment: self.submit_assignment_dialog(a),
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

    def open_drive_folder(self, folder_id):
        if self.drive_service:
            import webbrowser
            url = f"https://drive.google.com/drive/folders/{folder_id}"
            webbrowser.open(url)

    def upload_to_drive_dialog(self, assignment):
        drive_folder_id = assignment.get('drive_folder_id')
        if not drive_folder_id or not self.drive_service:
            self.show_snackbar("No Drive folder linked", ft.Colors.RED)
            return
        
        upload_status = ft.Text("")
        
        def on_file_picked(e: ft.FilePickerResultEvent):
            if not e.files:
                return
            
            file_path = e.files[0].path
            file_name = e.files[0].name
            
            
            student_name = self.current_student_email.split('@')[0] if self.current_student_email else "unknown"
            
            upload_status.value = f"Uploading {file_name}..."
            self.page.update()
            
            try:
            
                result = self.drive_service.upload_file(file_path, parent_id=drive_folder_id)
                
                if result:
                    upload_status.value = f"✅ Uploaded: {file_name}"
                    self.show_snackbar("File uploaded to Google Drive!", ft.Colors.GREEN)
                    
                    # Notify teacher
                    if self.notification_service:
                        self.notification_service.notify_submission_received(assignment, student_name)
                else:
                    upload_status.value = "❌ Upload failed"
                    self.show_snackbar("Upload failed", ft.Colors.RED)
            except Exception as ex:
                upload_status.value = f"❌ Error: {str(ex)}"
                self.show_snackbar(f"Error: {str(ex)}", ft.Colors.RED)
            
            self.page.update()
        
        file_picker = ft.FilePicker(on_result=on_file_picked)
        self.page.overlay.append(file_picker)
        
        folder_name = self.get_folder_name_by_id(drive_folder_id)
        
        dialog = ft.AlertDialog(
            title=ft.Text(f"Upload to: {folder_name}"),
            content=ft.Column([
                ft.Text(f"Assignment: {assignment.get('title')}"),
                ft.Text("Select a file to upload to the Google Drive folder.", size=14),
                ft.ElevatedButton(
                    "Choose File",
                    icon=ft.Icons.FILE_UPLOAD,
                    on_click=lambda e: file_picker.pick_files()
                ),
                upload_status
            ], height=150),
            actions=[
                ft.TextButton("Close", on_click=lambda e: self.close_dialog(dialog))
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def show_notifications_dialog(self):
        if not self.notification_service:
            return
        
        notifications = self.notification_service.get_notifications_for_student(self.current_student_email)
        notifications_list = ft.Column(scroll="auto", spacing=5)
        
        if not notifications:
            notifications_list.controls.append(ft.Text("No notifications", color=ft.Colors.GREY))
        else:
            for n in reversed(notifications[-20:]):  # Show last 20
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
                        on_click=lambda e, nid=n['id']: self.notification_service.mark_as_read(nid)
                    )
                )
        
        def mark_all_read(e):
            self.notification_service.mark_all_as_read(self.current_student_email)
            self.show_snackbar("All notifications marked as read", ft.Colors.BLUE)
            self.close_dialog(dialog)
            self.display_assignments()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Notifications"),
            content=ft.Container(content=notifications_list, width=400, height=300),
            actions=[
                ft.TextButton("Mark All Read", on_click=mark_all_read),
                ft.TextButton("Close", on_click=lambda e: self.close_dialog(dialog))
            ]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def add_assignment(self, e):
        title = self.assignment_title.value.strip()
        description = self.assignment_description.value.strip()
        subject = self.subject_dropdown.value
        max_score = self.max_score_field.value.strip()
        drive_folder_id = self.drive_folder_dropdown.value if self.drive_folder_dropdown.value != "none" else None
        target_for = self.target_dropdown.value or "all"  # all, bridging, regular
        
        if not title:
            self.show_snackbar("Please enter assignment title", ft.Colors.RED)
            return
        
        final_deadline = None
        if self.selected_date_value and self.selected_time_value:
            final_deadline = datetime.datetime.combine(self.selected_date_value, self.selected_time_value)
        elif self.selected_date_value:
            final_deadline = datetime.datetime.combine(self.selected_date_value, datetime.time(23, 59))
        
        new_assignment = {
            'id': str(datetime.datetime.now().timestamp()),
            'title': title,
            'description': description,
            'subject': subject or 'Other',
            'deadline': final_deadline.isoformat() if final_deadline else None,
            'max_score': max_score or '100',
            'attachment': self.selected_attachment["name"],
            'drive_folder_id': drive_folder_id,
            'target_for': target_for,  # who this assignment is for
            'created': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
            'status': 'Active'
        }
        
        self.assignments.append(new_assignment)
        self.save_json(self.assignments_file, self.assignments)
        
    
        if self.notification_service and self.students:
            self.notification_service.notify_new_assignment(new_assignment, self.students)
        

        self.assignment_title.value = ""
        self.assignment_description.value = ""
        self.subject_dropdown.value = None
        self.max_score_field.value = ""
        self.selected_deadline_display.value = "No deadline selected"
        self.selected_date_value = None
        self.selected_time_value = None
        self.attachment_text.value = "No file attached"
        self.selected_attachment["path"] = None
        self.selected_attachment["name"] = None
        self.drive_folder_dropdown.value = "none"
        
        self.display_assignments()
        self.show_snackbar("Assignment added! Students notified.", ft.Colors.GREEN)

    def delete_assignment(self, assignment):
        
        def confirm(e):
            self.assignments.remove(assignment)
            self.submissions = [s for s in self.submissions if s['assignment_id'] != assignment['id']]
            self.save_json(self.assignments_file, self.assignments)
            self.save_json(self.submissions_file, self.submissions)
            close_overlay(e)
            self.display_assignments()
            self.show_snackbar("Assignment deleted", ft.Colors.ORANGE)
        
        def close_overlay(e):
            if overlay in self.page.overlay:
                self.page.overlay.remove(overlay)
                self.page.update()
        
        overlay = ft.Container(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Confirm Delete", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Text(f"Delete '{assignment['title']}'?"),
                    ft.Text("This will also delete all submissions.", size=12, color=ft.Colors.GREY_600),
                    ft.Container(height=10),
                    ft.Row([
                        ft.TextButton("Cancel", on_click=close_overlay),
                        ft.ElevatedButton("Delete", on_click=confirm, bgcolor=ft.Colors.RED, color=ft.Colors.WHITE)
                    ], alignment=ft.MainAxisAlignment.END)
                ], tight=True, spacing=10),
                padding=25,
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                width=350,
                shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK))
            ),
            alignment=ft.alignment.center,
            expand=True,
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK)
        )
        
        self.page.overlay.append(overlay)
        self.page.update()

    def edit_assignment_dialog(self, assignment):
        
        title_field = ft.TextField(value=assignment['title'], label="Title", width=320)
        desc_field = ft.TextField(value=assignment.get('description', ''), label="Description", multiline=True, min_lines=2, width=320)
        score_field = ft.TextField(value=assignment.get('max_score', '100'), label="Max Score", width=100)
        
        drive_dropdown = ft.Dropdown(
            label="Drive Folder",
            value=assignment.get('drive_folder_id', 'none') or 'none',
            options=self._get_drive_folder_options(),
            width=200
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
            assignment['drive_folder_id'] = drive_dropdown.value if drive_dropdown.value != 'none' else None
            assignment['target_for'] = target_dropdown.value
            self.save_json(self.assignments_file, self.assignments)
            close_overlay(e)
            self.display_assignments()
            self.show_snackbar("Assignment updated", ft.Colors.BLUE)
        
        def close_overlay(e):
            if overlay in self.page.overlay:
                self.page.overlay.remove(overlay)
                self.page.update()
        
        overlay = ft.Container(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Edit Assignment", size=20, weight=ft.FontWeight.BOLD),
                        ft.IconButton(icon=ft.Icons.CLOSE, on_click=close_overlay)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(),
                    title_field,
                    desc_field,
                    ft.Row([score_field, target_dropdown], spacing=10),
                    drive_dropdown,
                    ft.Container(height=10),
                    ft.Row([
                        ft.TextButton("Cancel", on_click=close_overlay),
                        ft.ElevatedButton("Save", on_click=save, icon=ft.Icons.SAVE)
                    ], alignment=ft.MainAxisAlignment.END)
                ], spacing=10),
                padding=25,
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
                width=400,
                shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK))
            ),
            alignment=ft.alignment.center,
            expand=True,
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK)
        )
        
        self.page.overlay.append(overlay)
        self.page.update()

    def submit_assignment_dialog(self, assignment):
        submission_text = ft.TextField(
            hint_text="Submission notes/comments",
            multiline=True,
            min_lines=3
        )
        
        def submit(e):
            existing = self.get_submission_status(assignment['id'], self.current_student_email)
            
            if existing:
                existing['submission_text'] = submission_text.value
                existing['submitted_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            else:
                self.submissions.append({
                    'id': str(datetime.datetime.now().timestamp()),
                    'assignment_id': assignment['id'],
                    'student_email': self.current_student_email,
                    'submission_text': submission_text.value,
                    'submitted_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'grade': None,
                    'feedback': None
                })
            
            self.save_json(self.submissions_file, self.submissions)
            
            
            if self.notification_service:
                student_name = self.current_student_email.split('@')[0] if self.current_student_email else "Student"
                self.notification_service.notify_submission_received(assignment, student_name)
            
            dialog.open = False
            self.display_assignments()
            self.show_snackbar("Assignment submitted!", ft.Colors.GREEN)
        
        dialog = ft.AlertDialog(
            title=ft.Text(f"Submit: {assignment['title']}"),
            content=submission_text,
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog(dialog)),
                ft.ElevatedButton("Submit", on_click=submit)
            ]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def view_submissions_dialog(self, assignment):
        submissions_list = ft.Column(scroll="auto", spacing=10)
        
        assignment_submissions = [s for s in self.submissions if s['assignment_id'] == assignment['id']]
        
        if not assignment_submissions:
            submissions_list.controls.append(ft.Text("No submissions yet", color=ft.Colors.GREY))
        else:
            for sub in assignment_submissions:
                student_name = sub['student_email'].split('@')[0]
                
                grade_field = ft.TextField(
                    value=sub.get('grade', ''),
                    label="Grade",
                    width=100
                )
                feedback_field = ft.TextField(
                    value=sub.get('feedback', ''),
                    label="Feedback",
                    multiline=True,
                    expand=True
                )
                
                def save_grade(e, s=sub, g=grade_field, f=feedback_field):
                    s['grade'] = g.value
                    s['feedback'] = f.value
                    self.save_json(self.submissions_file, self.submissions)
                    
                    # Notify student
                    if self.notification_service and g.value:
                        self.notification_service.notify_grade_posted(assignment, s['student_email'], g.value)
                    
                    self.show_snackbar("Grade saved", ft.Colors.BLUE)
                
                card = ft.Container(
                    content=ft.Column([
                        ft.Text(f"Student: {student_name}", weight=ft.FontWeight.BOLD),
                        ft.Text(f"Submitted: {sub['submitted_at']}", size=12),
                        ft.Text(f"Notes: {sub.get('submission_text', 'No notes')}", size=12),
                        ft.Divider(),
                        ft.Row([grade_field, feedback_field]),
                        ft.ElevatedButton("Save Grade", on_click=save_grade, icon=ft.Icons.SAVE)
                    ]),
                    padding=10,
                    border=ft.border.all(1, ft.Colors.BLUE_GREY_200),
                    border_radius=8
                )
                submissions_list.controls.append(card)
        
        dialog = ft.AlertDialog(
            title=ft.Text(f"Submissions: {assignment['title']}"),
            content=ft.Container(content=submissions_list, width=600, height=400),
            actions=[ft.TextButton("Close", on_click=lambda e: self.close_dialog(dialog))]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def manage_students_dialog(self, e):
        students_list = ft.Column(scroll="auto", spacing=5)
        name_field = ft.TextField(label="Student Name", width=180)
        email_field = ft.TextField(label="Student Email", width=220)
        bridging_checkbox = ft.Checkbox(label="Bridging", value=False)
        
        def refresh_list():
            students_list.controls.clear()
            for student in self.students:
                bridging_badge = "[B] " if student.get('is_bridging', False) else ""
                students_list.controls.append(
                    ft.Row([
                        ft.Text(f"{bridging_badge}{student['name']} ({student['email']})", expand=True),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_color=ft.Colors.RED,
                            on_click=lambda e, s=student: remove_student(s),
                            tooltip="Remove student"
                        )
                    ])
                )
            self.page.update()
        
        def add_student(e):
            if name_field.value.strip() and email_field.value.strip():
                self.students.append({
                    'name': name_field.value.strip(),
                    'email': email_field.value.strip(),
                    'is_bridging': bridging_checkbox.value
                })
                self.save_json(self.students_file, self.students)
                name_field.value = ""
                email_field.value = ""
                bridging_checkbox.value = False
                refresh_list()
                self.update_student_dropdown()
                self.show_snackbar("Student added", ft.Colors.GREEN)
        
        def remove_student(student):
            self.students.remove(student)
            self.save_json(self.students_file, self.students)
            refresh_list()
            self.update_student_dropdown()
            self.show_snackbar("Student removed", ft.Colors.ORANGE)
        
        refresh_list()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Manage Students"),
            content=ft.Container(
                content=ft.Column([
                    ft.Row([name_field, email_field, bridging_checkbox]),
                    ft.ElevatedButton("Add Student", on_click=add_student, icon=ft.Icons.ADD),
                    ft.Divider(),
                    ft.Row([
                        ft.Text("Current Students:", weight=ft.FontWeight.BOLD),
                        ft.Text("[B] = Bridging Student", size=11, color=ft.Colors.GREY_600)
                    ]),
                    students_list
                ]),
                width=550,
                height=400
            ),
            actions=[ft.TextButton("Close", on_click=lambda e: self.close_dialog(dialog))]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def show_snackbar(self, message, color=ft.Colors.BLUE):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=color)
        self.page.snack_bar.open = True
        self.page.update()

    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()

    def switch_mode(self, e):
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

    def update_student_dropdown(self):
        options = []
        for s in self.students:
            if s.get('is_bridging', False):
                options.append(ft.dropdown.Option(s['email'], f"[B] {s['name']}"))
            else:
                options.append(ft.dropdown.Option(s['email'], s['name']))
        
        self.student_dropdown.options = options
        
        self.student_dropdown.options.insert(0, ft.dropdown.Option("__register__", "📝 Register New Account"))
        self.page.update()

    def register_student_dialog(self, e=None):
        
        name_field = ft.TextField(label="Your Full Name", autofocus=True, width=300)
        email_field = ft.TextField(label="Your Email (Gmail required)", width=300)
        student_id_field = ft.TextField(label="Student ID (required)", width=300)
        bridging_switch = ft.Switch(label="I am a Bridging Student", value=False)
        error_text = ft.Text("", color=ft.Colors.RED, size=12)
        
        
        overlay_container = ft.Container(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("📝 Student Registration", size=20, weight=ft.FontWeight.BOLD),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            on_click=lambda e: self._close_registration_overlay(overlay_container)
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text("Register to access assignments and submit your work.", size=14),
                    ft.Divider(),
                    name_field,
                    email_field,
                    student_id_field,
                    ft.Container(
                        content=bridging_switch,
                        padding=ft.padding.only(top=10, bottom=5)
                    ),
                    ft.Text("Bridging students are those transferring or taking additional courses.", 
                           size=11, color=ft.Colors.GREY_600, italic=True),
                    error_text,
                    ft.Row([
                        ft.TextButton("Cancel", on_click=lambda e: self._close_registration_overlay(overlay_container)),
                        ft.ElevatedButton(
                            "Register", 
                            icon=ft.Icons.PERSON_ADD,
                            on_click=lambda e: self._do_register(
                                name_field, email_field, student_id_field, 
                                bridging_switch, error_text, overlay_container
                            )
                        )
                    ], alignment=ft.MainAxisAlignment.END)
                ], spacing=10),
                padding=30,
                bgcolor=ft.Colors.WHITE,
                border_radius=15,
                width=420,
                shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK))
            ),
            alignment=ft.alignment.center,
            expand=True,
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK)
        )
        
        self.page.overlay.append(overlay_container)
        self.page.update()
    
    def _close_registration_overlay(self, overlay):
        if overlay in self.page.overlay:
            self.page.overlay.remove(overlay)
            self.page.update()
    
    def _do_register(self, name_field, email_field, student_id_field, bridging_switch, error_text, overlay):
        name = name_field.value.strip() if name_field.value else ""
        email = email_field.value.strip() if email_field.value else ""
        student_id = student_id_field.value.strip() if student_id_field.value else ""
        is_bridging = bridging_switch.value
        
        print(f"DEBUG: Registering - Name: {name}, Email: {email}, Bridging: {is_bridging}")
        
        if not name:
            error_text.value = "Please enter your full name"
            self.page.update()
            return
        
        
        if not student_id:
            error_text.value = "Student ID is required"
            self.page.update()
            return
        
        
        is_valid, error_msg = self._validate_email(email)
        if not is_valid:
            error_text.value = error_msg
            self.page.update()
            return
        
        
        if not email.lower().endswith('@gmail.com'):
            error_text.value = "Only Gmail accounts are accepted"
            self.page.update()
            return
        
        
        if any(s.get('email') == email for s in self.students):
            error_text.value = "This email is already registered"
            self.page.update()
            return
        
        
        new_student = {
            'name': name,
            'email': email,
            'student_id': student_id if student_id else None,
            'is_bridging': is_bridging,
            'registered_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        
        
        self.students.append(new_student)
        self.save_json(self.students_file, self.students)
        
        student_type = "Bridging Student" if is_bridging else "Regular Student"
        print(f"DEBUG: {student_type} saved to students.json")
        
        
        self._close_registration_overlay(overlay)
        
        
        
        self.update_student_dropdown()
        self.student_dropdown.value = email
        self.current_student_email = email
        
        self.display_assignments()
        self.show_snackbar(f"Welcome, {name}! Registered as {student_type}.", ft.Colors.GREEN)

    def on_student_selected(self, e):
        if self.student_dropdown.value == "__register__":
            self.student_dropdown.value = None
            self.register_student_dialog()
            return
        self.current_student_email = self.student_dropdown.value
        self.display_assignments()

    def get_view(self):
        
        
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
            on_click=self.add_assignment,
            icon=ft.Icons.ADD,
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE)
        )
        
        self.form_container = ft.Container(
            content=ft.Column([
                ft.Text("Create New Assignment", size=20, weight=ft.FontWeight.BOLD),
                self.assignment_title,
                ft.Row([self.subject_dropdown, self.max_score_field, self.target_dropdown]),
                self.assignment_description,
                ft.Row([ft.Text("Link to Drive:", size=14), self.drive_folder_dropdown], spacing=10),
                ft.Row([attach_btn, self.attachment_text], spacing=10),
                ft.Row([pick_deadline_btn, self.selected_deadline_display], spacing=10),
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
            on_click=self.manage_students_dialog,
            icon=ft.Icons.PEOPLE,
            visible=self.current_mode == "teacher"
        )
        
        return ft.Column([
            ft.Container(
                content=ft.Row([
                    back_btn,
                    ft.Icon(ft.Icons.SCHOOL, size=40, color=ft.Colors.BLUE),
                    ft.Text("Learning Management System", size=28, weight=ft.FontWeight.BOLD),
                ], alignment=ft.MainAxisAlignment.START),
                padding=20
            ),
            
            ft.Container(
                content=ft.Row([
                    self.mode_label,
                    self.mode_switch,
                    ft.Container(expand=True),
                    self.manage_students_btn
                ]),
                padding=10,
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLUE),
                border_radius=10
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
