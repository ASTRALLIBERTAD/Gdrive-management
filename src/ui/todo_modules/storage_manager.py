import flet as ft
import json
import os
from utils.ui_components import DialogManager, FormField
from utils.advanced_ui import ProgressIndicator, EmptyStateBuilder
from utils.common import show_snackbar


class NotificationHelper:
    def __init__(self, page):
        self.page = page
    
    def success(self, message):
        show_snackbar(self.page, message, ft.Colors.GREEN)
    
    def error(self, message):
        show_snackbar(self.page, message, ft.Colors.RED)
    
    def warning(self, message):
        show_snackbar(self.page, message, ft.Colors.ORANGE)


class FolderHelper:
    def __init__(self, drive_service):
        self.drive_service = drive_service
    
    def get_or_create_folder(self, parent_id, folder_name):
        if not self.drive_service:
            return None
        try:
            results = self.drive_service.list_files(folder_id=parent_id)
            files = results.get('files', []) if results else []
            for f in files:
                if f.get('name') == folder_name and f.get('mimeType') == 'application/vnd.google-apps.folder':
                    return f
            return self.drive_service.create_folder(folder_name, parent_id=parent_id)
        except:
            return None


class UploadHelper:
    def __init__(self, drive_service):
        self.drive_service = drive_service
    
    def upload_with_path(self, file_path, root_id, folder_path, file_name):
        if not self.drive_service:
            return None
        current_id = root_id
        folder_helper = FolderHelper(self.drive_service)
        for folder_name in folder_path:
            folder = folder_helper.get_or_create_folder(current_id, folder_name)
            if folder:
                current_id = folder.get('id', current_id)
        return self.drive_service.upload_file(file_path, parent_id=current_id)
    
    def upload_with_metadata(self, file_path, parent_id, student_name, file_name):
        if not self.drive_service:
            return None
        return self.drive_service.upload_file(file_path, parent_id=parent_id)


class ConfigHelper:
    @staticmethod
    def set_value(filename, key, value):
        data = {}
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
            except:
                pass
        data[key] = value
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)


class StorageManager:
    def __init__(self, todo_view, drive_service):
        self.todo = todo_view
        self.drive_service = drive_service
        self.folder_hierarchy_mgr = FolderHelper(drive_service) if drive_service else None
        self.upload_mgr = UploadHelper(drive_service) if drive_service else None
        self.dialog_mgr = DialogManager(todo_view.page)
        self.notif_mgr = NotificationHelper(todo_view.page)
    
    def get_or_create_subject_folder_in_lms(self, subject):
        if not self.folder_hierarchy_mgr or not self.todo.data_manager.lms_root_id:
            return None
        
        return self.folder_hierarchy_mgr.get_or_create_folder(
            self.todo.data_manager.lms_root_id,
            subject
        )
    
    def upload_assignment_attachment(self, file_path, file_name, subject, assignment_id):
        if not self.upload_mgr or not self.todo.data_manager.lms_root_id:
            return None
        
        try:
            folder_path = [subject, 'Attachments']
            prefixed_name = f"ATTACH_{assignment_id}_{file_name}"
            
            return self.upload_mgr.upload_with_path(
                file_path,
                self.todo.data_manager.lms_root_id,
                folder_path,
                prefixed_name
            )
        except Exception as e:
            print(f"Error uploading attachment: {e}")
            return None
    
    def upload_submission_to_link_drive(self, file_path, file_name, subject, student_name, link_drive_id):
        if not self.upload_mgr or not link_drive_id:
            return None
        
        try:
            return self.upload_mgr.upload_with_metadata(
                file_path,
                link_drive_id,
                student_name,
                file_name
            )
        except Exception as e:
            print(f"Error uploading submission: {e}")
            return None
    
    def show_storage_settings(self):
        if not self.drive_service:
            self.notif_mgr.error("Drive service not available")
            return
        
        current_folder_name = "Not Set (Using Local Storage)"
        lms_root_id = self.todo.data_manager.lms_root_id
        
        if lms_root_id:
            try:
                info = self.drive_service.get_file_info(lms_root_id)
                if info:
                    current_folder_name = info.get('name', 'Unknown')
            except:
                current_folder_name = "Invalid ID"
        
        def unlink_drive(e):
            self._unlink_drive_folder()
            close_overlay(e)
        
        def select_drive(e):
            close_overlay(e)
            self.select_drive_folder_dialog()
        
        content = ft.Column([
            ft.Text(f"Current LMS Data Folder: {current_folder_name}", weight=ft.FontWeight.BOLD),
            ft.Text("Select a shared folder where all students and teachers have access."),
            ft.Divider(),
            ft.ElevatedButton("Select/Change Drive Folder", on_click=select_drive, icon=ft.Icons.FOLDER),
            ft.ElevatedButton("Unlink (Use Local)", on_click=unlink_drive, color=ft.Colors.RED, icon=ft.Icons.LINK_OFF)
        ], tight=True)
        
        overlay, close_overlay = self.dialog_mgr.show_overlay(content, "Storage Settings")
    
    def _unlink_drive_folder(self):
        ConfigHelper.set_value("lms_config.json", "lms_root_id", None)
        
        self.todo.data_manager.lms_root_id = None
        self.notif_mgr.warning("Unlinked Drive folder. Using local storage.")
        
        self.todo.students = self.todo.data_manager.load_students()
        self.todo.student_manager.update_student_dropdown()
        self.todo.display_assignments()
    
    def select_drive_folder_dialog(self):
        from utils.validators import StringUtils
        
        try:
            folders = self.drive_service.list_files(folder_id='root', use_cache=False)
        except Exception as e:
            self.notif_mgr.error(f"Error listing folders: {e}")
            return
        
        folder_list = folders.get('files', []) if folders else []
        folder_list = [f for f in folder_list if f['mimeType'] == 'application/vnd.google-apps.folder']
        
        list_view = ft.ListView(expand=True, spacing=10, height=300)
        
        def perform_search(query):
            results = self.drive_service.search_files(query, use_cache=False)
            update_list([f for f in results if f['mimeType'] == 'application/vnd.google-apps.folder'])
        
        def update_list(items):
            list_view.controls.clear()
            
            if not items:
                list_view.controls.append(
                    EmptyStateBuilder.create(
                        ft.Icons.FOLDER_OFF,
                        "No folders found",
                        "Try searching for a different name"
                    )
                )
            else:
                for f in items:
                    list_view.controls.append(
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.FOLDER, color=ft.Colors.BLUE),
                            title=ft.Text(f['name']),
                            on_click=lambda e, folder=f: on_select(folder)
                        )
                    )
            
            if list_view.page:
                list_view.update()
        
        def on_select(folder):
            self._save_lms_root(folder['id'])
            self.notif_mgr.success(f"Linked to '{folder['name']}'")
            close_overlay(None)
            
            self.todo.assignments = self.todo.data_manager.load_assignments()
            self.todo.students = self.todo.data_manager.load_students()
            self.todo.submissions = self.todo.data_manager.load_submissions()
            self.todo.display_assignments()
        
        def process_link(e):
            link = link_field.value.strip() if link_field.value else ""
            if not link:
                return
            
            file_id = StringUtils.extract_id_from_url(link)
            
            if not file_id:
                self.notif_mgr.error("Could not extract ID from link")
                return
            
            try:
                info = self.drive_service.get_file_info(file_id)
                if info and info.get('mimeType') == 'application/vnd.google-apps.folder':
                    on_select({'id': file_id, 'name': info.get('name', 'Unknown')})
                else:
                    self.notif_mgr.error("ID is not a valid folder or access denied")
            except Exception as ex:
                self.notif_mgr.error(f"Error checking Link: {ex}")
        
        search_field = FormField.create_text_field(
            hint_text="Search folders...",
            expand=True
        )
        search_field.on_submit = lambda e: perform_search(e.control.value)
        
        link_field = FormField.create_text_field(
            hint_text="Paste Drive Link or Folder ID",
            expand=True
        )
        link_field.on_submit = process_link
        
        link_btn = ft.IconButton(icon=ft.Icons.ARROW_FORWARD, on_click=process_link, tooltip="Use Link")
        
        content = ft.Column([
            ft.Row([link_field, link_btn]),
            ft.Text("- OR -", size=10, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            search_field,
            list_view
        ], height=450)
        
        update_list(folder_list)
        
        overlay, close_overlay = self.dialog_mgr.show_overlay(content, "Select Drive Folder", width=500)
    
    def _save_lms_root(self, folder_id):
        ConfigHelper.set_value("lms_config.json", "lms_root_id", folder_id)
        self.todo.data_manager.lms_root_id = folder_id
    
    def create_browse_dialog(self, initial_parent_id, on_select):
        from utils.advanced_ui import NavigationBar
        
        current_folder = {'id': initial_parent_id, 'name': 'Root'}
        if initial_parent_id == 'root':
            current_folder['name'] = 'My Drive'
        elif self.drive_service:
            try:
                info = self.drive_service.get_file_info(initial_parent_id)
                if info:
                    current_folder = info
            except:
                pass
        
        file_list = ft.Column(scroll="auto", height=300)
        current_path_text = ft.Text(f"Current: {current_folder['name']}", weight=ft.FontWeight.BOLD)
        loading_indicator = ft.ProgressBar(width=None, visible=False)
        
        def load_folder(folder_id, initial=False):
            ProgressIndicator.show_in_container(
                ft.Container(content=file_list),
                "Loading folders..."
            )
            loading_indicator.visible = True
            file_list.controls.clear()
            self.todo.page.update()
            
            try:
                results = self.drive_service.list_files(folder_id=folder_id, use_cache=True)
                files = results.get('files', []) if results else []
                folders = [f for f in files if f['mimeType'] == 'application/vnd.google-apps.folder']
                
                if (folder_id == 'root' or folder_id == initial_parent_id) and self.todo.saved_links:
                    file_list.controls.append(ft.Container(
                        content=ft.Text("⭐ Saved Folders", weight=ft.FontWeight.BOLD),
                        padding=ft.padding.only(left=10, top=10, bottom=5)
                    ))
                    for link in self.todo.saved_links:
                        if link.get("mimeType") == "application/vnd.google-apps.folder":
                            file_list.controls.append(
                                ft.ListTile(
                                    leading=ft.Icon(ft.Icons.FOLDER_SPECIAL, color=ft.Colors.AMBER),
                                    title=ft.Text(link.get("name", "Unknown")),
                                    subtitle=ft.Text("Saved Link"),
                                    on_click=lambda e, fid=link["id"], fname=link["name"]: enter_folder(fid, fname),
                                    trailing=ft.IconButton(ft.Icons.CHECK, on_click=lambda e, fid=link["id"]: confirm_selection(fid))
                                )
                            )
                    file_list.controls.append(ft.Divider())
                
                if folder_id != 'root' and folder_id != initial_parent_id:
                    file_list.controls.append(
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.ARROW_UPWARD),
                            title=ft.Text(".. (Up)"),
                            on_click=lambda e: load_parent(folder_id)
                        )
                    )
                
                if not folders:
                    file_list.controls.append(
                        EmptyStateBuilder.create(
                            ft.Icons.FOLDER_OFF,
                            "No subfolders found"
                        )
                    )
                else:
                    for f in folders:
                        file_list.controls.append(
                            ft.ListTile(
                                leading=ft.Icon(ft.Icons.FOLDER, color=ft.Colors.BLUE),
                                title=ft.Text(f['name']),
                                subtitle=ft.Text("Click to open"),
                                on_click=lambda e, fid=f['id'], fname=f['name']: enter_folder(fid, fname),
                                trailing=ft.IconButton(ft.Icons.CHECK, on_click=lambda e, fid=f['id']: confirm_selection(fid))
                            )
                        )
                    
            except Exception as e:
                file_list.controls.append(ft.Text(f"Error: {e}", color=ft.Colors.RED))
            
            loading_indicator.visible = False
            self.todo.page.update()
        
        def enter_folder(fid, fname):
            current_path_text.value = f"Current: {fname}"
            current_folder['id'] = fid
            current_folder['name'] = fname
            load_folder(fid)
        
        def load_parent(current_id):
            current_path_text.value = f"Current: {current_folder['name']}"
            load_folder(initial_parent_id)
        
        def confirm_selection(fid):
            on_select(fid)
            close_func(None)
        
        content = ft.Column([
            current_path_text,
            loading_indicator,
            file_list,
            ft.Divider(),
            ft.Row([
                ft.TextButton("Cancel", on_click=lambda e: close_func(None)),
                ft.ElevatedButton(
                    "Select Current Folder", 
                    on_click=lambda e: confirm_selection(current_folder['id']),
                    icon=ft.Icons.CHECK
                )
            ], alignment=ft.MainAxisAlignment.END)
        ])
        
        load_folder(initial_parent_id, initial=True)
        
        overlay, close_func = self.dialog_mgr.show_overlay(content, "Select Folder", width=400, height=500)
    
    def open_new_assignment_folder_picker(self, e):
        start_id = self.todo.selected_drive_folder_id or self.todo.data_manager.lms_root_id or 'root'
        self.create_browse_dialog(start_id, self.update_new_assignment_folder)
    
    def update_new_assignment_folder(self, fid):
        self.todo.selected_drive_folder_id = fid
        name = self.todo.get_folder_name_by_id(fid)
        
        if name == "Linked Folder" and self.drive_service:
            try:
                info = self.drive_service.get_file_info(fid)
                if info:
                    name = info.get('name', name)
            except:
                pass
        
        self.todo.drive_folder_label.value = f"Selected: {name}"
        self.todo.page.update()