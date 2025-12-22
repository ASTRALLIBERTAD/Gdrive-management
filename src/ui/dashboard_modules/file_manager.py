import flet as ft
from utils.advanced_ui import ListItemBuilder
from utils.ui_components import DialogManager
from utils.common import show_snackbar


class NotificationHelper:
    def __init__(self, page):
        self.page = page
    
    def success(self, message):
        show_snackbar(self.page, message, ft.Colors.GREEN)
    
    def error(self, message):
        show_snackbar(self.page, message, ft.Colors.RED)


class FileManager:
    def __init__(self, dashboard):
        self.dash = dashboard
        self.dialog_mgr = DialogManager(dashboard.page)
        self.notif_mgr = NotificationHelper(dashboard.page)
        
        try:
            from services.file_preview_service import FilePreviewService
            self.file_preview = FilePreviewService(dashboard.page, dashboard.drive)
        except ImportError:
            self.file_preview = None

    def show_menu(self, item, is_folder=False, is_shared_drive=False):
        menu_items = []
        
        if not is_folder and self.file_preview:
            menu_items.append(
                ft.PopupMenuItem(text="Preview", on_click=lambda e: self.preview_file(item))
            )
        
        menu_items.extend([
            ft.PopupMenuItem(text="Info", on_click=lambda e: self.show_file_info(item)),
            ft.PopupMenuItem(text="Rename", on_click=lambda e: self._rename_file_dialog(item)),
            ft.PopupMenuItem(text="Delete", on_click=lambda e: self._delete_file_dialog(item)),
        ])
        
        return menu_items

    def create_folder_item(self, folder, subfolder_count, is_shared_drive=False):
        return ListItemBuilder.create_folder_item(
            folder,
            subfolder_count,
            on_click=lambda f: self.open_folder(f, is_shared_drive),
            on_menu=lambda f: self.show_menu(f, is_folder=True, is_shared_drive=is_shared_drive)
        )
    
    def create_file_item(self, file):
        from utils.file_operations import MimeTypeHelper
        
        is_folder = MimeTypeHelper.is_folder(file.get("mimeType"))
        
        return ListItemBuilder.create_file_item(
            file,
            on_click=lambda f: self.handle_file_click(f),
            on_menu=lambda f: self.show_menu(f, is_folder=is_folder),
            show_preview=self.preview_file if self.file_preview and not is_folder else None
        )
    
    def preview_file(self, file):
        if self.file_preview and not file.get("mimeType") == "application/vnd.google-apps.folder":
            self.file_preview.show_preview(
                file_id=file.get("id"),
                file_name=file.get("name", "File")
            )
    
    def open_folder(self, folder, is_shared_drive=False):
        self.dash.show_folder_contents(folder["id"], folder.get("name", folder["id"]), is_shared_drive)
    
    def handle_file_click(self, file):
        from utils.file_operations import MimeTypeHelper
        
        if MimeTypeHelper.is_folder(file.get("mimeType")):
            self.dash.show_folder_contents(file["id"], file["name"])
        else:
            self.preview_file(file)
    
    def show_folder_menu(self, folder, is_shared_drive=False):
        self.open_folder(folder, is_shared_drive)
    
    def _rename_file_dialog(self, file):
        from utils.ui_components import FormField
        from utils.validators import Validator
        
        name_field = FormField.create_text_field(value=file["name"], expand=True)
        
        def rename(e):
            new_name = name_field.value.strip()
            
            if Validator.is_empty(new_name):
                self.notif_mgr.error("Name cannot be empty")
                return
            
            if new_name != file["name"]:
                result = self.dash.drive.rename_file(file["id"], new_name)
                if result:
                    self.dash.refresh_folder_contents()
                    self.notif_mgr.success(f"Renamed to '{new_name}'")
                else:
                    self.notif_mgr.error("Failed to rename")
            
            close_overlay(e)
        
        content = ft.Column([
            name_field,
            ft.Row([
                ft.TextButton("Cancel", on_click=lambda e: close_overlay(e)),
                ft.ElevatedButton("Rename", on_click=rename, icon=ft.Icons.SAVE)
            ], alignment=ft.MainAxisAlignment.END)
        ], spacing=15)
        
        overlay, close_overlay = self.dialog_mgr.show_overlay(content, "Rename", width=400)
    
    def _delete_file_dialog(self, file):
        def delete():
            if self.dash.drive.delete_file(file["id"]):
                self.dash.refresh_folder_contents()
                self.notif_mgr.success("Deleted successfully")
            else:
                self.notif_mgr.error("Failed to delete")
        
        self.dialog_mgr.show_confirmation(
            "Confirm Delete",
            f"Delete '{file.get('name', '')}'?",
            delete,
            "Delete",
            "Cancel",
            ft.Colors.RED
        )
    
    def show_file_info(self, file):
        from utils.file_operations import FileOperations
        
        info = self.dash.drive.get_file_info(file["id"]) if isinstance(file, dict) and "id" in file else file
        if not info:
            return
        
        size_str = FileOperations.format_size(info.get('size')) if info.get('size') else "N/A"
        
        def on_preview(e):
            self.preview_file(info)
            close_overlay(e)
        
        def on_browser(e):
            from utils.common import open_drive_file
            open_drive_file(info.get('id'))
        
        buttons = []
        if self.file_preview:
            buttons.append(
                ft.ElevatedButton("Preview", icon=ft.Icons.VISIBILITY, on_click=on_preview)
            )
        buttons.append(
            ft.ElevatedButton("Open in Browser", icon=ft.Icons.OPEN_IN_NEW, on_click=on_browser)
        )
        
        content = ft.Column([
            ft.Text(f"Name: {info.get('name', 'N/A')}"),
            ft.Text(f"Type: {info.get('mimeType', 'N/A')}"),
            ft.Text(f"Size: {size_str}"),
            ft.Text(f"Modified: {info.get('modifiedTime', 'N/A')[:10]}"),
            ft.Divider(),
            ft.Row(buttons, spacing=10),
            ft.Row([
                ft.TextButton("Close", on_click=lambda e: close_overlay(e))
            ], alignment=ft.MainAxisAlignment.END)
        ], tight=True, spacing=10)
        
        overlay, close_overlay = self.dialog_mgr.show_overlay(content, "File Information", width=400)
    
    def create_new_folder_dialog(self):
        from utils.ui_components import FormField
        from utils.validators import Validator
        from utils.advanced_ui import ProgressIndicator
        
        name_field = FormField.create_text_field(label="Folder name", expand=True)
        status_container = ft.Container()

        def create(e):
            folder_name = name_field.value.strip() if name_field.value else ""
            
            if Validator.is_empty(folder_name):
                self.notif_mgr.error("Folder name is required")
                return
            
            status_container.content = ProgressIndicator.create_loading("Creating folder...")
            self.dash.page.update()

            folder = self.dash.drive.create_folder(folder_name, parent_id=self.dash.current_folder_id)
            
            if folder:
                close_overlay(e)
                
                new_folder_item = self.create_folder_item({
                    'id': folder['id'],
                    'name': folder['name'],
                    'mimeType': 'application/vnd.google-apps.folder'
                }, 0)
                
                insert_position = 1
                if len(self.dash.folder_list.controls) > insert_position:
                    self.dash.folder_list.controls.insert(insert_position, new_folder_item)
                else:
                    self.dash.folder_list.controls.append(new_folder_item)

                self.dash.drive._invalidate_cache(self.dash.current_folder_id)
                self.notif_mgr.success(f"Created folder '{folder_name}'")
                self.dash.page.update()
            else:
                status_container.content = ft.Text("Failed to create folder", color=ft.Colors.RED)
                self.dash.page.update()
        
        content = ft.Column([
            name_field,
            status_container,
            ft.Row([
                ft.TextButton("Cancel", on_click=lambda e: close_overlay(e)),
                ft.ElevatedButton("Create", on_click=create, icon=ft.Icons.CREATE_NEW_FOLDER),
            ], alignment=ft.MainAxisAlignment.END)
        ], spacing=15)

        overlay, close_overlay = self.dialog_mgr.show_overlay(content, "Create New Folder", width=350)
    
    def select_file_to_upload(self):
        def on_result(e: ft.FilePickerResultEvent):
            if not e.files:
                return
            
            for f in e.files:
                result = self.dash.drive.upload_file(f.path, parent_id=self.dash.current_folder_id)
                if result:
                    self.notif_mgr.success(f"Uploaded {f.name}")
                else:
                    self.notif_mgr.error(f"Failed to upload {f.name}")
            
            self.dash.refresh_folder_contents()

        file_picker = ft.FilePicker(on_result=on_result)
        self.dash.page.overlay.append(file_picker)
        self.dash.page.update()
        file_picker.pick_files()