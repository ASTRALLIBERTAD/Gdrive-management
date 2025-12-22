import flet as ft


class DialogManager:
    def __init__(self, page):
        self.page = page
    
    def show_overlay(self, content, title=None, width=400, height=None):
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
    
    def show_snackbar(self, message, color=ft.Colors.BLUE):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=color)
        self.page.snack_bar.open = True
        self.page.update()
    
    def show_confirmation(self, title, message, on_confirm, confirm_text="Confirm", cancel_text="Cancel", confirm_color=ft.Colors.BLUE):
        def confirm(e):
            close_overlay(e)
            on_confirm()
        
        content = ft.Column([
            ft.Text(message),
            ft.Container(height=10),
            ft.Row([
                ft.TextButton(cancel_text, on_click=lambda e: close_overlay(e)),
                ft.ElevatedButton(confirm_text, on_click=confirm, bgcolor=confirm_color, color=ft.Colors.WHITE)
            ], alignment=ft.MainAxisAlignment.END)
        ], tight=True, spacing=10)
        
        overlay, close_overlay = self.show_overlay(content, title, width=350)


class FormField:
    @staticmethod
    def create_text_field(label=None, hint_text=None, multiline=False, expand=True, width=None, **kwargs):
        return ft.TextField(
            label=label,
            hint_text=hint_text,
            multiline=multiline,
            expand=expand,
            width=width,
            **kwargs
        )
    
    @staticmethod
    def create_dropdown(label=None, hint_text=None, options=None, width=None, **kwargs):
        return ft.Dropdown(
            label=label,
            hint_text=hint_text,
            options=options or [],
            width=width,
            **kwargs
        )
    
    @staticmethod
    def create_file_picker(page, on_result):
        file_picker = ft.FilePicker(on_result=on_result)
        page.overlay.append(file_picker)
        page.update()
        return file_picker


class CardBuilder:
    @staticmethod
    def create_container(content, padding=10, border_radius=10, bgcolor=None, border_color=None):
        return ft.Container(
            content=content,
            padding=padding,
            border_radius=border_radius,
            bgcolor=bgcolor,
            border=ft.border.all(1, border_color) if border_color else None
        )
    
    @staticmethod
    def create_status_badge(text, color):
        return ft.Container(
            content=ft.Text(text, size=12, color=ft.Colors.WHITE),
            bgcolor=color,
            padding=5,
            border_radius=5
        )
    
    @staticmethod
    def create_icon_text_row(icon, text, icon_color=None, text_size=13):
        return ft.Row([
            ft.Icon(icon, size=16, color=icon_color),
            ft.Text(text, size=text_size)
        ])