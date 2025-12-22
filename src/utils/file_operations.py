import os
from pathlib import Path


class FileOperations:
    @staticmethod
    def format_size(size_bytes):
        if size_bytes is None:
            return "Unknown size"
        try:
            size = int(size_bytes)
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} PB"
        except (ValueError, TypeError):
            return "Unknown size"
    
    @staticmethod
    def get_file_extension(filename):
        return os.path.splitext(filename)[1].lower()
    
    @staticmethod
    def get_unique_filename(directory, filename):
        path = Path(directory) / filename
        
        if not path.exists():
            return filename
        
        name_parts = os.path.splitext(filename)
        counter = 1
        
        while path.exists():
            new_filename = f"{name_parts[0]} ({counter}){name_parts[1]}"
            path = Path(directory) / new_filename
            counter += 1
        
        return path.name
    
    @staticmethod
    def ensure_directory(directory):
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def read_file(filepath, mode='r', encoding='utf-8'):
        try:
            with open(filepath, mode, encoding=encoding if mode == 'r' else None) as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {filepath}: {e}")
            return None
    
    @staticmethod
    def write_file(filepath, content, mode='w', encoding='utf-8'):
        try:
            with open(filepath, mode, encoding=encoding if mode == 'w' else None) as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing file {filepath}: {e}")
            return False


class MimeTypeHelper:
    MIME_TYPES = {
        'folder': 'application/vnd.google-apps.folder',
        'document': 'application/vnd.google-apps.document',
        'spreadsheet': 'application/vnd.google-apps.spreadsheet',
        'presentation': 'application/vnd.google-apps.presentation',
        'pdf': 'application/pdf',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'image': 'image/',
        'text': 'text/'
    }
    
    @staticmethod
    def is_folder(mime_type):
        return mime_type == MimeTypeHelper.MIME_TYPES['folder']
    
    @staticmethod
    def is_image(mime_type):
        return mime_type and mime_type.startswith(MimeTypeHelper.MIME_TYPES['image'])
    
    @staticmethod
    def is_text(mime_type):
        return mime_type and mime_type.startswith(MimeTypeHelper.MIME_TYPES['text'])
    
    @staticmethod
    def is_pdf(mime_type):
        return mime_type == MimeTypeHelper.MIME_TYPES['pdf']
    
    @staticmethod
    def get_icon_for_mime(mime_type):
        import flet as ft
        
        if MimeTypeHelper.is_folder(mime_type):
            return ft.Icons.FOLDER, ft.Colors.BLUE
        elif MimeTypeHelper.is_image(mime_type):
            return ft.Icons.IMAGE, ft.Colors.GREEN
        elif MimeTypeHelper.is_pdf(mime_type):
            return ft.Icons.PICTURE_AS_PDF, ft.Colors.RED
        elif mime_type == MimeTypeHelper.MIME_TYPES['docx']:
            return ft.Icons.DESCRIPTION, ft.Colors.BLUE
        elif mime_type == MimeTypeHelper.MIME_TYPES['xlsx']:
            return ft.Icons.TABLE_CHART, ft.Colors.GREEN
        elif mime_type == MimeTypeHelper.MIME_TYPES['pptx']:
            return ft.Icons.SLIDESHOW, ft.Colors.ORANGE
        else:
            return ft.Icons.INSERT_DRIVE_FILE, ft.Colors.GREY