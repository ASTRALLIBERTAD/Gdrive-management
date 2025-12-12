import flet as ft
import json
import os

FAVORITES_FILE = "favorites.json"


class FavoritesManager:
    def __init__(self, dashboard):
        self.dash = dashboard
        self.favorites = self.load_favorites()
    
    def load_favorites(self):
        if os.path.exists(FAVORITES_FILE):
            try:
                with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def save_favorites(self):
        try:
            with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
                json.dump(self.favorites, f, indent=2)
        except:
            pass
    
    def add_favorite(self, subject, folder_id, folder_name):
        self.favorites.setdefault(subject, [])
        if any(f["id"] == folder_id for f in self.favorites[subject]):
            return False
        self.favorites[subject].append({"id": folder_id, "name": folder_name})
        self.save_favorites()
        return True
    
    def remove_favorite(self, subject, folder_id):
        if subject not in self.favorites:
            return False
        self.favorites[subject] = [f for f in self.favorites[subject] if f["id"] != folder_id]
        if not self.favorites[subject]:
            del self.favorites[subject]
        self.save_favorites()
        return True
    
    def open_save_favorite_dialog(self):
        subject_field = ft.TextField(label="Subject / Category", autofocus=True)

        def save(e):
            subject = subject_field.value.strip()
            if not subject:
                return
            added = self.add_favorite(subject, self.dash.current_folder_id, self.dash.current_folder_name)
            self.dash.page.snack_bar = ft.SnackBar(ft.Text("Saved to favorites" if added else "Already in favorites"))
            self.dash.page.snack_bar.open = True
            dialog.open = False
            self.dash.page.update()

        dialog = ft.AlertDialog(title=ft.Text("Save folder to favorites"), content=subject_field, actions=[ft.TextButton("Cancel", on_click=lambda e: self.dash.close_dialog(dialog)), ft.ElevatedButton("Save", on_click=save)])

        self.dash.page.dialog = dialog
        dialog.open = True
        self.dash.page.update()
    
    def build_favorites_ui(self):
        col = ft.Column(spacing=6)
        if not self.favorites:
            col.controls.append(ft.Text("No saved links", color=ft.Colors.GREY_600))
            return col
        for subject, folders in self.favorites.items():
            subject_row = ft.Row([
                ft.Text(subject),
                ft.IconButton(icon=ft.Icons.DELETE, on_click=lambda e, s=subject: self.remove_subject_confirm(s)),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            col.controls.append(subject_row)
            for f in folders:
                folder_row = ft.Row([
                    ft.Text(f.get("name", f.get("id")), expand=True),
                    ft.IconButton(icon=ft.Icons.OPEN_IN_NEW, on_click=lambda e, fid=f["id"], nm=f.get("name", ""): self.dash.folder_navigator.show_folder_contents(fid, nm)),
                    ft.IconButton(icon=ft.Icons.DELETE, on_click=lambda e, s=subject, fid=f["id"]: self.confirm_remove_favorite(s, fid)),
                ])
                col.controls.append(folder_row)
        return col
    
    def remove_subject_confirm(self, subject):
        def remove(e):
            if subject in self.favorites:
                del self.favorites[subject]
                self.save_favorites()
            dialog.open = False
            self.dash.page.update()
        dialog = ft.AlertDialog(title=ft.Text("Remove subject"), content=ft.Text(f"Remove all favorites under '{subject}'?"), actions=[ft.TextButton("Cancel", on_click=lambda e: self.dash.close_dialog(dialog)), ft.ElevatedButton("Remove", on_click=remove, bgcolor=ft.Colors.RED)])

        self.dash.page.dialog = dialog
        dialog.open = True
        self.dash.page.update()
    
    def confirm_remove_favorite(self, subject, folder_id):
        def remove(e):
            self.remove_favorite(subject, folder_id)
            dialog.open = False
            self.dash.page.update()
        dialog = ft.AlertDialog(title=ft.Text("Remove favorite"), content=ft.Text("Remove this saved folder?"), actions=[ft.TextButton("Cancel", on_click=lambda e: self.dash.close_dialog(dialog)), ft.ElevatedButton("Remove", on_click=remove, bgcolor=ft.Colors.RED)])

        self.dash.page.dialog = dialog
        dialog.open = True
        self.dash.page.update()