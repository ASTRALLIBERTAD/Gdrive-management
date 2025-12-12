import flet as ft
import json
import os


class StorageManager:
    def __init__(self, todo_view, drive_service):
        self.todo = todo_view
        self.drive_service = drive_service
    
    def show_storage_settings(self):
        
        if not self.drive_service:
            self.todo.show_snackbar("Drive service not available", ft.Colors.RED)
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
            ft.ElevatedButton("Select/Change Drive Folder", on_click=select_drive),
            ft.ElevatedButton("Unlink (Use Local)", on_click=unlink_drive, color=ft.Colors.RED)
        ], tight=True)
        
        overlay, close_overlay = self.todo.show_overlay(content, "Storage Settings")
    
    def _unlink_drive_folder(self):
        config_file = "lms_config.json"
        config = {}
        
        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except:
                pass
        
        config["lms_root_id"] = None
        
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        
        self.todo.data_manager.lms_root_id = None
        self.todo.show_snackbar("Unlinked Drive folder. Using local storage.", ft.Colors.ORANGE)
        
        self.todo.students = self.todo.data_manager.load_students()
        self.todo.student_manager.update_student_dropdown()
        self.todo.display_assignments()
    
    def select_drive_folder_dialog(self):
        try:
            folders = self.drive_service.list_files(folder_id='root', use_cache=False)
        except Exception as e:
            self.todo.show_snackbar(f"Error listing folders: {e}", ft.Colors.RED)
            return
        
        folder_list = folders.get('files', []) if folders else []
        folder_list = [f for f in folder_list if f['mimeType'] == 'application/vnd.google-apps.folder']
        
        list_view = ft.ListView(expand=True, spacing=10, height=300)
        
        def perform_search(query):
            results = self.drive_service.search_files(query, use_cache=False)
            update_list([f for f in results if f['mimeType'] == 'application/vnd.google-apps.folder'])
        
        def update_list(items):
            list_view.controls.clear()
            for f in items:
                list_view.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.FOLDER),
                        title=ft.Text(f['name']),
                        on_click=lambda e, folder=f: on_select(folder)
                    )
                )
            if list_view.page:
                list_view.update()
        
        def on_select(folder):
            self._save_lms_root(folder['id'])
            self.todo.show_snackbar(f"Linked to '{folder['name']}'", ft.Colors.GREEN)
            close_overlay(None)
            
            self.todo.assignments = self.todo.data_manager.load_assignments()
            self.todo.students = self.todo.data_manager.load_students()
            self.todo.submissions = self.todo.data_manager.load_submissions()
            self.todo.display_assignments()
        
        def process_link(e):
            link = link_field.value.strip() if link_field.value else ""
            if not link:
                return
            
            file_id = None
            
            if "/folders/" in link:
                try:
                    parts = link.split("/folders/")
                    if len(parts) > 1:
                        file_id = parts[1].split('?')[0].split('/')[0]
                except:
                    pass
            elif "id=" in link:
                try:
                    parts = link.split("id=")
                    if len(parts) > 1:
                        file_id = parts[1].split('&')[0]
                except:
                    pass
            elif len(link) > 20 and "/" not in link:
                file_id = link
            
            if not file_id:
                self.todo.show_snackbar("Could not extract ID from link", ft.Colors.RED)
                return
            
            try:
                info = self.drive_service.get_file_info(file_id)
                if info and info.get('mimeType') == 'application/vnd.google-apps.folder':
                    on_select({'id': file_id, 'name': info.get('name', 'Unknown')})
                else:
                    self.todo.show_snackbar("ID is not a valid folder or access denied", ft.Colors.RED)
            except Exception as ex:
                self.todo.show_snackbar(f"Error checking Link: {ex}", ft.Colors.RED)
        
        search_field = ft.TextField(
            hint_text="Search folders...",
            on_submit=lambda e: perform_search(e.control.value)
        )
        link_field = ft.TextField(
            hint_text="Paste Drive Link or Folder ID",
            expand=True,
            text_size=12,
            on_submit=process_link
        )
        link_btn = ft.IconButton(icon=ft.Icons.ARROW_FORWARD, on_click=process_link, tooltip="Use Link")
        
        content = ft.Column([
            ft.Row([link_field, link_btn]),
            ft.Text("- OR -", size=10, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            search_field,
            list_view
        ], height=450)
        
        update_list(folder_list)
        
        overlay, close_overlay = self.todo.show_overlay(content, "Select Drive Folder", width=500)
    
    def _save_lms_root(self, folder_id):
        config_file = "lms_config.json"
        config = {}
        
        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except:
                pass
        
        config["lms_root_id"] = folder_id
        
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        
        self.todo.data_manager.lms_root_id = folder_id
    
    def create_browse_dialog(self, initial_parent_id, on_select):
        
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
                
                
                for f in folders:
                    file_list.controls.append(
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.FOLDER),
                            title=ft.Text(f['name']),
                            subtitle=ft.Text("Click to open"),
                            on_click=lambda e, fid=f['id'], fname=f['name']: enter_folder(fid, fname),
                            trailing=ft.IconButton(ft.Icons.CHECK, on_click=lambda e, fid=f['id']: confirm_selection(fid))
                        )
                    )
                
                if not folders:
                    file_list.controls.append(ft.Text("No subfolders found."))
                    
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
                ft.ElevatedButton("Select Current Folder", 
                                 on_click=lambda e: confirm_selection(current_folder['id']))
            ], alignment=ft.MainAxisAlignment.END)
        ])
        
        load_folder(initial_parent_id, initial=True)
        
        overlay, close_func = self.todo.show_overlay(content, "Select Folder", width=400, height=500)
    
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