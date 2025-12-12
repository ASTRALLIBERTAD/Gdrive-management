import flet as ft
import base64
import mimetypes


class FilePreview:

    def __init__(self, page, drive_service=None):
        self.page = page
        self.drive_service = drive_service
    
    def show_preview(self, file_id=None, file_path=None, file_name="File"):
        preview_content = ft.Column(scroll="auto", expand=True)
        loading = ft.ProgressRing()
        
        content_container = ft.Container(
            content=ft.Column([loading], alignment=ft.MainAxisAlignment.CENTER),
            width=700,
            height=500
        )
        
        def close_preview(e):
            if overlay in self.page.overlay:
                self.page.overlay.remove(overlay)
                self.page.update()
        
        overlay = ft.Container(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(file_name, size=18, weight=ft.FontWeight.BOLD),
                        ft.IconButton(icon=ft.Icons.CLOSE, on_click=close_preview)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(),
                    content_container
                ], tight=True),
                padding=20,
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                width=750,
                height=600,
                shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK))
            ),
            alignment=ft.alignment.center,
            expand=True,
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK)
        )
        
        self.page.overlay.append(overlay)
        self.page.update()
        
        if file_id and self.drive_service:
            self._load_from_drive(file_id, file_name, content_container, loading)
        elif file_path:
            self._load_from_path(file_path, file_name, content_container, loading)
        else:
            content_container.content = ft.Text("No file to preview", color=ft.Colors.RED)
            self.page.update()
    
    def _load_from_drive(self, file_id, file_name, container, loading):
        try:

            file_info = self.drive_service.get_file_info(file_id)
            mime_type = file_info.get('mimeType', '')
            
            import io
            from googleapiclient.http import MediaIoBaseDownload
            
            request = self.drive_service.service.files().get_media(fileId=file_id)
            file_buffer = io.BytesIO()
            downloader = MediaIoBaseDownload(file_buffer, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            file_buffer.seek(0)
            file_data = file_buffer.read()
            
            self._render_preview(file_data, mime_type, file_name, container, loading)
            
        except Exception as e:
            container.content = ft.Column([
                ft.Icon(ft.Icons.ERROR, size=48, color=ft.Colors.RED),
                ft.Text(f"Error loading file: {str(e)}", color=ft.Colors.RED),
                ft.ElevatedButton(
                    "Open in Browser",
                    icon=ft.Icons.OPEN_IN_NEW,
                    on_click=lambda e: self._open_in_browser(file_id)
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            self.page.update()
    
    def _load_from_path(self, file_path, file_name, container, loading):
        try:
            mime_type, _ = mimetypes.guess_type(file_path)
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            self._render_preview(file_data, mime_type, file_name, container, loading)
            
        except Exception as e:
            container.content = ft.Column([
                ft.Icon(ft.Icons.ERROR, size=48, color=ft.Colors.RED),
                ft.Text(f"Error loading file: {str(e)}", color=ft.Colors.RED)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            self.page.update()
    
    def _render_preview(self, file_data, mime_type, file_name, container, loading):

        preview_widget = None
        
        if mime_type and mime_type.startswith('image/'):
            
            base64_data = base64.b64encode(file_data).decode()
            preview_widget = ft.Image(
                src_base64=base64_data,
                fit=ft.ImageFit.CONTAIN,
                width=650,
                height=450
            )
        
        elif mime_type == 'application/pdf':
            size_mb = len(file_data) / (1024 * 1024)
            preview_widget = ft.Column([
                ft.Icon(ft.Icons.PICTURE_AS_PDF, size=100, color=ft.Colors.RED),
                ft.Text("PDF Document", size=20, weight=ft.FontWeight.BOLD),
                ft.Text(f"Size: {size_mb:.2f} MB"),
                ft.Text("PDF preview is not available in-app", italic=True),
                ft.Divider(),
                ft.ElevatedButton(
                    "Download PDF",
                    icon=ft.Icons.DOWNLOAD,
                    on_click=lambda e: self._download_file(file_data, file_name)
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
        
        elif mime_type and mime_type.startswith('text/'):
            try:
                text_content = file_data.decode('utf-8')
                preview_widget = ft.Container(
                    content=ft.Text(text_content, selectable=True),
                    padding=10,
                    bgcolor=ft.Colors.GREY_100,
                    border_radius=5,
                    width=650,
                    height=450
                )
            except:
                preview_widget = ft.Text("Cannot decode text file", color=ft.Colors.RED)
        
        elif mime_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            size_mb = len(file_data) / (1024 * 1024)
            preview_widget = ft.Column([
                ft.Icon(ft.Icons.DESCRIPTION, size=100, color=ft.Colors.BLUE),
                ft.Text("Word Document", size=20, weight=ft.FontWeight.BOLD),
                ft.Text(f"Size: {size_mb:.2f} MB"),
                ft.Text("Word preview is not available in-app", italic=True),
                ft.Divider(),
                ft.ElevatedButton(
                    "Download Document",
                    icon=ft.Icons.DOWNLOAD,
                    on_click=lambda e: self._download_file(file_data, file_name)
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
        
        else:
            
            size_mb = len(file_data) / (1024 * 1024)
            preview_widget = ft.Column([
                ft.Icon(ft.Icons.INSERT_DRIVE_FILE, size=100, color=ft.Colors.GREY),
                ft.Text("File Preview Not Available", size=20, weight=ft.FontWeight.BOLD),
                ft.Text(f"Type: {mime_type or 'Unknown'}"),
                ft.Text(f"Size: {size_mb:.2f} MB"),
                ft.Divider(),
                ft.ElevatedButton(
                    "Download File",
                    icon=ft.Icons.DOWNLOAD,
                    on_click=lambda e: self._download_file(file_data, file_name)
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
        
        container.content = ft.Column([preview_widget], 
                                      scroll="auto",
                                      horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.page.update()
    
    def _download_file(self, file_data, file_name):

        try:
            import os
            from pathlib import Path
            
            
            downloads_path = Path.home() / "Downloads" / file_name
            
            with open(downloads_path, 'wb') as f:
                f.write(file_data)
            
            self._show_snackbar(f"Downloaded to: {downloads_path}", ft.Colors.GREEN)
        except Exception as e:
            self._show_snackbar(f"Download failed: {str(e)}", ft.Colors.RED)
    
    def _open_in_browser(self, file_id):
        import webbrowser
        webbrowser.open(f"https://drive.google.com/file/d/{file_id}/view")
    
    def _show_snackbar(self, message, color):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=color)
        self.page.snack_bar.open = True
        self.page.update()