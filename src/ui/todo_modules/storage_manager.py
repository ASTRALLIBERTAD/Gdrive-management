"""Storage Manager Module.

This module provides an interface for interacting with the Google Drive storage
backend specific to the LMS structure. It handles folder creation, hierarchy management
(LMS Root -> Subject -> Attachments), file uploading, and the selection of
Drive folders via the UI.

Classes:
    StorageManager: Manages file and folder operations in Google Drive.
"""

import flet as ft
import json
import os

from utils.common import show_snackbar


class StorageManager:
    """Manages Google Drive storage operations for the LMS.

    Purpose / Responsibility:
        Orchestrates folder hierarchy creation and file uploads within the LMS Google Drive structure.
        It handles creating Subject folders, managing Attachments subfolders, and linking
        student submissions to specific Drive locations. It maximizes efficiency by caching
        folder IDs to reduce API calls.

    Attributes:
        todo (TodoView): Reference to the main application view for accessing shared state (like DataManager).
        drive_service (DriveService): The service wrapper for making Google Drive API calls.
        subject_folders_cache (dict): In-memory cache mapping subject names to Drive Folder IDs.

    Interactions / Calls:
        - Calls `src.services.drive_service.DriveService` for all cloud operations.
        - Accesses `todo.data_manager.lms_root_id` to determine the root folder.
        - Updates `todo.assignments` and other UI states after storage changes.

    Algorithm / Pseudocode:
        1. Initialize with `todo_view` and `drive_service`.
        2. `get_or_create_subject_folder`: Check cache -> check Drive -> create if missing -> update cache.
        3. `upload_assignment_attachment`: Get subject folder -> ensure 'Attachments' subfolder -> upload file.
        4. `select_drive_folder_dialog`: List/Search Drive folders -> User selects -> Link as LMS Root.

    Examples:
        >>> storage = StorageManager(todo_view, drive_service)
        >>> folder_id = storage.get_or_create_subject_folder_in_lms("Physics")
        >>> storage.upload_assignment_attachment("test.pdf", "test.pdf", "Physics", "123")

    See Also:
        - :class:`~src.services.drive_service.DriveService`
        - :class:`~src.ui.todo_modules.data_manager.DataManager`
    """
    def __init__(self, todo_view, drive_service):
        """Initialize the StorageManager.

        Purpose:
            Sets up the storage manager with necessary service references and initializes the cache.

        Args:
            todo_view (TodoView): Parent view instance for accessing global state.
            drive_service (DriveService): Service instance for Drive API operations.

        Interactions:
            - Stores references to `todo_view` and `drive_service`.
            - Initializes `subject_folders_cache` as empty dict.
        """
        self.todo = todo_view
        self.drive_service = drive_service
        self.subject_folders_cache = {}
    
    def get_or_create_subject_folder_in_lms(self, subject):
        """Retrieve or create a folder for a specific subject within the LMS root.

        Purpose:
            Ensures a dedicated folder exists for the given subject to organize files.
            Utilizes caching to prevent redundant API calls for the same subject.

        Args:
            subject (str): Name of the subject (e.g., 'Mathematics').

        Returns:
            str | None: The Drive Folder ID if successful, else None.

        Interactions:
            - Reads `todo.data_manager.lms_root_id`.
            - Calls `drive_service.list_files` (to find existing).
            - Calls `drive_service.create_folder` (if missing).

        Algorithm:
            1. Check if Drive Service and LMS Root are configured.
            2. Check `subject_folders_cache` for existing ID.
            3. If cached, verify validity (optional) and return.
            4. If not cached:
               a. List files in LMS Root filtering by name=`subject`.
               b. If found, update cache and return ID.
               c. If not found, create new folder, update cache, and return ID.
        """
        if not self.drive_service or not self.todo.data_manager.lms_root_id:
            return None
        
        cache_key = f"lms_{subject}"
        if cache_key in self.subject_folders_cache:
            folder_id = self.subject_folders_cache[cache_key]
            try:
                info = self.drive_service.get_file_info(folder_id)
                if info:
                    return folder_id
            except:
                pass
        
        lms_root = self.todo.data_manager.lms_root_id
        
        try:
            result = self.drive_service.list_files(folder_id=lms_root, use_cache=False)
            files = result.get('files', []) if result else []
            
            for f in files:
                if f.get('name') == subject and f.get('mimeType') == 'application/vnd.google-apps.folder':
                    self.subject_folders_cache[cache_key] = f['id']
                    return f['id']
            
            new_folder = self.drive_service.create_folder(subject, parent_id=lms_root)
            if new_folder:
                self.subject_folders_cache[cache_key] = new_folder['id']
                return new_folder['id']
        except Exception as e:
            print(f"Error creating subject folder in LMS: {e}")
        
        return None
    
    def upload_assignment_attachment(self, file_path, file_name, subject, assignment_id):
        """Upload an attachment file to the subject's 'Attachments' subfolder.

        Purpose:
            Organizes assignment files by placing them into a specific 'Attachments' subdirectory
            under the relevant Subject folder.

        Args:
            file_path (str): Local path to the file to upload.
            file_name (str): Desired filename in Drive.
            subject (str): The subject this assignment belongs to.
            assignment_id (str): Assignment ID used to prefix the filename for uniqueness.

        Returns:
            dict | None: The uploaded file object (metadata) from Drive API, or None.

        Interactions:
            - Calls `get_or_create_subject_folder_in_lms`.
            - Calls `_get_or_create_attachments_folder_in_lms`.
            - Calls `drive_service.upload_file`.

        Algorithm:
            1. Get ID for Subject folder.
            2. Get ID for 'Attachments' subfolder within Subject folder.
            3. Construct prefixed filename: `ATTACH_{id}_{name}`.
            4. Upload file to 'Attachments' folder.
        """
        if not self.drive_service or not self.todo.data_manager.lms_root_id:
            return None
        
        subject_folder_id = self.get_or_create_subject_folder_in_lms(subject)
        if not subject_folder_id:
            return None
        
        try:
            attachments_folder_id = self._get_or_create_attachments_folder_in_lms(subject_folder_id)
            if not attachments_folder_id:
                return None
            
            prefixed_name = f"ATTACH_{assignment_id}_{file_name}"
            
            result = self.drive_service.upload_file(
                file_path,
                parent_id=attachments_folder_id,
                file_name=prefixed_name
            )
            
            return result
        except Exception as e:
            print(f"Error uploading attachment: {e}")
            return None
    
    def _get_or_create_attachments_folder_in_lms(self, subject_folder_id):
        """Find or create the 'Attachments' folder within a subject folder.

        Purpose:
            Helper method to ensure the standard 'Attachments' subdirectory exists.

        Args:
            subject_folder_id (str): The Drive ID of the parent subject folder.

        Returns:
            str | None: Folder ID of 'Attachments', or None on error.
        """
        try:
            result = self.drive_service.list_files(folder_id=subject_folder_id, use_cache=False)
            files = result.get('files', []) if result else []
            
            for f in files:
                if f.get('name') == 'Attachments' and f.get('mimeType') == 'application/vnd.google-apps.folder':
                    return f['id']
            
            new_folder = self.drive_service.create_folder('Attachments', parent_id=subject_folder_id)
            if new_folder:
                return new_folder['id']
        except Exception as e:
            print(f"Error creating attachments folder: {e}")
        
        return None
    
    def upload_submission_to_link_drive(self, file_path, file_name, subject, student_name, link_drive_id):
        """Upload a student submission to a specific Drive folder.

        Purpose:
            Handles the upload of student work to a designated assignment folder (linked folder).

        Args:
            file_path (str): Local path to the submission file.
            file_name (str): Original filename.
            subject (str): Subject name (for context/logging).
            student_name (str): Name of the student (for file prefixing).
            link_drive_id (str): The target Drive Folder ID where submissions go.

        Returns:
            dict | None: Uploaded file metadata or None.

        Interactions:
            - Calls `drive_service.upload_file`.

        Algorithm:
            1. Verify Drive Service and Target Folder ID.
            2. Construct filename: `{student_name}_{file_name}`.
            3. Upload to `link_drive_id`.
        """
        if not self.drive_service or not link_drive_id:
            return None
        
        try:
            prefixed_name = f"{student_name}_{file_name}"
            
            result = self.drive_service.upload_file(
                file_path,
                parent_id=link_drive_id,
                file_name=prefixed_name
            )
            
            return result
        except Exception as e:
            print(f"Error uploading submission: {e}")
            return None
    
    def show_storage_settings(self):
        """Show configuration dialog for LMS storage settings.

        Purpose:
            Provides a UI for the user to view the current LMS Root folder status
            and choose to Link (select from Drive) or Unlink (use local only).

        Interactions:
            - Calls `todo.show_overlay`.
            - Calls `select_drive_folder_dialog` (if requested).
            - Calls `_unlink_drive_folder` (if requested).

        Algorithm:
            1. Check current `lms_root_id`.
            2. If set, fetch its name via Drive API.
            3. Build UI: Display current folder name.
            4. Buttons: "Select/Change Drive Folder", "Unlink".
            5. Helper functions bind actions to close overlay and proceed.
        """
        if not self.drive_service:
            show_snackbar(self.todo.page, "Drive service not available", ft.Colors.RED)
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
        
        # Show data sync status
        sync_status_text = "❌ Not syncing"
        if self.drive_service and lms_root_id:
            sync_status_text = "✓ Syncing with Drive"
        
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
            ft.Row([
                ft.Icon(ft.Icons.CLOUD_SYNC, size=20),
                ft.Text(f"Data Sync: {sync_status_text}", size=14, weight=ft.FontWeight.BOLD)
            ]),
            ft.Text("When enabled, assignments, students, submissions, and notifications sync automatically.", 
                   size=12, color=ft.Colors.GREY_600, italic=True),
            ft.Divider(),
            ft.ElevatedButton("Select/Change Drive Folder", on_click=select_drive),
            ft.ElevatedButton("Unlink (Use Local)", on_click=unlink_drive, color=ft.Colors.RED)
        ], tight=True)
        
        overlay, close_overlay = self.todo.show_overlay(content, "Storage Settings")
    
    def _unlink_drive_folder(self):
        """Remove the link to the Google Drive root folder.

        Purpose:
            Resets the application to use local storage only by removing the LMS Root ID from config.

        Interactions:
            - Reads/Writes `lms_config.json`.
            - Updates `todo.data_manager.lms_root_id`.
            - Refreshes UI (Assignments, Students).
        """
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
        
        # Update notification service
        if self.todo.notification_service:
            self.todo.update_lms_root_id(None)
        
        show_snackbar(self.todo.page, "Unlinked Drive folder. Using local storage.", ft.Colors.ORANGE)
        
        self.todo.students = self.todo.data_manager.load_students()
        self.todo.student_manager.update_student_dropdown()
        self.todo.display_assignments()
    
    def select_drive_folder_dialog(self):
        """Open an overlay for searching and selecting a Drive folder.

        Purpose:
            Provides a comprehensive UI to browse, search, or paste a link to select a folder
            to serve as the LMS Root.

        Interactions:
            - Lists files via `drive_service.list_files`.
            - Searches via `drive_service.search_files`.
            - calls `_save_lms_root` on selection.

        Algorithm:
            1. List root folders.
            2. Build ListView of folders.
            3. Provide Search Bar (filters list).
            4. Provide "Paste Link" field (extracts ID).
            5. On Select: Save ID, Close Overlay, Reload Data.
        """
        try:
            folders = self.drive_service.list_files(folder_id='root', use_cache=False)
        except Exception as e:
            show_snackbar(self.todo.page, f"Error listing folders: {e}", ft.Colors.RED)
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
            show_snackbar(self.todo.page, f"Linked to '{folder['name']}'", ft.Colors.GREEN)
            close_overlay(None)
            
            self.todo.assignments = self.todo.data_manager.load_assignments()
            self.todo.students = self.todo.data_manager.load_students()
            self.todo.submissions = self.todo.data_manager.load_submissions()
            
            # Update and sync notification service
            if self.todo.notification_service:
                self.todo.update_lms_root_id(folder['id'])
            
            self.todo.student_manager.update_student_dropdown()
            self.todo.display_assignments()
            show_snackbar(self.todo.page, "✓ All data synced with Drive", ft.Colors.BLUE)
        
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
                show_snackbar(self.todo.page, "Could not extract ID from link", ft.Colors.RED)
                return
            
            try:
                info = self.drive_service.get_file_info(file_id)
                if info and info.get('mimeType') == 'application/vnd.google-apps.folder':
                    on_select({'id': file_id, 'name': info.get('name', 'Unknown')})
                else:
                    show_snackbar(self.todo.page, "ID is not a valid folder or access denied", ft.Colors.RED)
            except Exception as ex:
                show_snackbar(self.todo.page, f"Error checking Link: {ex}", ft.Colors.RED)
        
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
        """Update and persist the LMS root folder ID in local config.

        Purpose:
            Saves the selected folder ID to `lms_config.json` so it persists across restarts.

        Args:
            folder_id (str): The Drive folder ID.

        Interactions:
            - Writes to `lms_config.json`.
            - Updates in-memory `todo.data_manager.lms_root_id`.
        """
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
        """Open an overlay to browse and select a Drive folder.

        Purpose:
            A reusable file browser dialog that allows traversing the Drive folder hierarchy
            to select a specific destination (e.g., for assignment submissions).

        Args:
            initial_parent_id (str): Starting folder ID (or 'root').
            on_select (Callable): Callback function `fn(selected_id)` to execute on selection.

        Interactions:
            - Calls `drive_service.list_files` (recursive navigation).
            - Updates UI dynamic list.

        Algorithm:
            1. `load_folder(id)`: Fetch children folders.
            2. Display "Up" button if not root.
            3. Display children as click-to-enter tiles.
            4. "Select Current Folder" button returns current ID.
            5. Checkmark icon on tile returns that specific folder's ID.
        """
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
        """Invoke dialog to select a target Drive folder for an assignment.

        Purpose:
            Trigger handler for the "Select Linked Folder" button in the assignment form.

        Args:
            e (ft.ControlEvent): Trigger event.

        Interactions:
            - Calls `create_browse_dialog`.
        """
        start_id = self.todo.selected_drive_folder_id or self.todo.data_manager.lms_root_id or 'root'
        self.create_browse_dialog(start_id, self.update_new_assignment_folder)
    
    def update_new_assignment_folder(self, fid):
        """Update the UI with the selected folder's name.

        Purpose:
            Callback used by the folder picker to update the assignment form state.

        Args:
            fid (str): Selected Drive folder ID.

        Interactions:
            - Calls `drive_service.get_file_info` (to show name).
            - Updates `todo.drive_folder_label`.
            - Updates `todo.selected_drive_folder_id`.
        """
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