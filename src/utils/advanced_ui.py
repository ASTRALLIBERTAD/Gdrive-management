import flet as ft


class ListItemBuilder:
    @staticmethod
    def create_file_item(file, on_click=None, on_menu=None, show_preview=None):
        from utils.file_operations import MimeTypeHelper, FileOperations
        
        is_folder = MimeTypeHelper.is_folder(file.get("mimeType"))
        icon, color = MimeTypeHelper.get_icon_for_mime(file.get("mimeType"))
        size_str = "Folder" if is_folder else FileOperations.format_size(file.get("size"))
        
        action_buttons = []
        if show_preview and not is_folder:
            action_buttons.append(
                ft.IconButton(
                    icon=ft.Icons.VISIBILITY,
                    tooltip="Preview",
                    on_click=lambda e: show_preview(file)
                )
            )
        
        if on_menu:
            action_buttons.append(ft.PopupMenuButton(items=on_menu(file)))
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, size=24, color=color),
                ft.Column([
                    ft.Text(file.get("name", "Untitled"), size=14),
                    ft.Text(size_str, size=12, color=ft.Colors.GREY_600),
                ], expand=True),
                *action_buttons
            ]),
            padding=10,
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_200)),
            on_click=lambda e: on_click(file) if on_click else None,
        )
    
    @staticmethod
    def create_folder_item(folder, subfolder_count=0, on_click=None, on_menu=None):
        from utils.validators import StringUtils
        
        folder_name = folder.get("name", "Untitled")
        display_name = StringUtils.truncate(folder_name, 40)
        
        menu_items = on_menu(folder) if on_menu else []
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.FOLDER, size=24, color=ft.Colors.BLUE),
                ft.Column([
                    ft.Text(display_name, size=14),
                    ft.Text(f"{subfolder_count} folders", size=12, color=ft.Colors.GREY_600),
                ], expand=True),
                ft.PopupMenuButton(items=menu_items) if menu_items else ft.Container(),
            ]),
            padding=10,
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_300)),
            on_click=lambda e: on_click(folder) if on_click else None,
        )
    
    @staticmethod
    def create_student_item(student, on_remove=None):
        bridging_badge = "[B] " if student.get('is_bridging', False) else ""
        
        return ft.Row([
            ft.Text(f"{bridging_badge}{student['name']} ({student['email']})", expand=True),
            ft.IconButton(
                icon=ft.Icons.DELETE,
                icon_color=ft.Colors.RED,
                on_click=lambda e: on_remove(student) if on_remove else None,
                tooltip="Remove student"
            ) if on_remove else ft.Container()
        ])
    
    @staticmethod
    def create_notification_item(notification, on_click=None):
        is_unread = not notification.get('read', False)
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.CIRCLE, size=8,
                           color=ft.Colors.BLUE if is_unread else ft.Colors.GREY),
                    ft.Text(notification.get('title', 'Notification'),
                           weight=ft.FontWeight.BOLD if is_unread else ft.FontWeight.NORMAL),
                ]),
                ft.Text(notification.get('message', ''), size=12),
                ft.Text(notification.get('created_at', ''), size=10, color=ft.Colors.GREY),
            ]),
            padding=8,
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLUE) if is_unread else None,
            border_radius=5,
            on_click=lambda e: on_click(notification) if on_click else None
        )


class ProgressIndicator:
    @staticmethod
    def create_loading(message="Loading..."):
        return ft.Row([
            ft.ProgressRing(width=20, height=20),
            ft.Text(message, size=14)
        ])
    
    @staticmethod
    def show_in_container(container, message="Loading..."):
        container.content = ProgressIndicator.create_loading(message)
        return container


class NavigationBar:
    @staticmethod
    def create_breadcrumb(current_name, on_back=None, on_refresh=None, extra_buttons=None):
        controls = []
        
        if on_back:
            controls.append(ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=on_back))
        
        controls.append(ft.Text(current_name, size=18, weight=ft.FontWeight.BOLD))
        
        if on_refresh:
            controls.append(
                ft.ElevatedButton("Refresh", icon=ft.Icons.REFRESH, on_click=on_refresh)
            )
        
        if extra_buttons:
            controls.extend(extra_buttons)
        
        return ft.Row(controls, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    @staticmethod
    def create_tabs(tabs_config, active_tab=None, on_tab_click=None):
        buttons = []
        for tab in tabs_config:
            is_active = tab.get('id') == active_tab
            buttons.append(
                ft.ElevatedButton(
                    tab['label'],
                    on_click=lambda e, t=tab: on_tab_click(t) if on_tab_click else None,
                    bgcolor=ft.Colors.BLUE if is_active else None,
                    color=ft.Colors.WHITE if is_active else None
                )
            )
        
        return ft.Container(
            content=ft.Row(buttons, spacing=10, alignment=ft.MainAxisAlignment.CENTER),
            padding=10
        )


class InputValidator:
    @staticmethod
    def apply_validation_state(field, is_valid, error_message="Required"):
        if is_valid:
            field.error_text = None
            field.border_color = None
        else:
            field.error_text = error_message
            field.border_color = ft.Colors.RED
    
    @staticmethod
    def clear_validation(fields):
        for field in fields:
            field.error_text = None
            field.border_color = None


class StateManager:
    def __init__(self):
        self._state = {}
        self._listeners = {}
    
    def set(self, key, value):
        old_value = self._state.get(key)
        self._state[key] = value
        
        if key in self._listeners and old_value != value:
            for listener in self._listeners[key]:
                listener(value, old_value)
    
    def get(self, key, default=None):
        return self._state.get(key, default)
    
    def subscribe(self, key, callback):
        if key not in self._listeners:
            self._listeners[key] = []
        self._listeners[key].append(callback)
    
    def unsubscribe(self, key, callback):
        if key in self._listeners:
            self._listeners[key].remove(callback)


class AsyncHandler:
    @staticmethod
    def run_with_loading(page, task_func, on_complete=None, on_error=None, loading_message="Processing..."):
        loading = ft.AlertDialog(
            content=ft.Row([
                ft.ProgressRing(),
                ft.Text(loading_message)
            ]),
            modal=True
        )
        
        page.dialog = loading
        loading.open = True
        page.update()
        
        def execute():
            try:
                result = task_func()
                page.dialog.open = False
                page.update()
                
                if on_complete:
                    on_complete(result)
            except Exception as e:
                page.dialog.open = False
                page.update()
                
                if on_error:
                    on_error(e)
                else:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Error: {str(e)}"),
                        bgcolor=ft.Colors.RED
                    )
                    page.snack_bar.open = True
                    page.update()
        
        import threading
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()


class EmptyStateBuilder:
    @staticmethod
    def create(icon, message, action_text=None, on_action=None):
        controls = [
            ft.Icon(icon, size=64, color=ft.Colors.GREY_400),
            ft.Text(message, size=16, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER)
        ]
        
        if action_text and on_action:
            controls.append(
                ft.ElevatedButton(action_text, on_click=on_action)
            )
        
        return ft.Container(
            content=ft.Column(
                controls,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20
            ),
            padding=40,
            alignment=ft.alignment.center
        )