import flet as ft
import os
from pathlib import Path

def register_fcm_for_user(page: ft.Page, user_email: str):
    if page.platform != ft.PagePlatform.ANDROID:
        print(f"FCM only available on Android (current: {page.platform})")
        return False

    try:
        email_file = "fcm_email.txt"

        safe_email = user_email.replace("@", "_").replace(".", "_")

        with open(email_file, "w") as f:
            f.write(safe_email)

        print(f"✓ Saved email for FCM: {safe_email}")
        print(f"  File location: {email_file}")
        print(f"  MainActivity will read this file and register FCM token")

        return True
    except Exception as e:
        print(f"✗ Error saving email for FCM: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_saved_email(page: ft.Page):
    if page.platform != ft.PagePlatform.ANDROID:
        return None
    
    try:
        email_file = Path("fcm_email.txt")
        
        if email_file.exists():
            with open(email_file, 'r') as f:
                email = f.read().strip()
                print(f"✓ Found saved email: {email}")
                return email
        else:
            print("⚠ No saved email found yet")
            return None
            
    except Exception as e:
        print(f"✗ Error reading saved email: {e}")
        return None


def clear_saved_email(page: ft.Page):
    if page.platform != ft.PagePlatform.ANDROID:
        return False
    
    try:
        email_file = Path("fcm_email.txt")
        
        if email_file.exists():
            email_file.unlink()
            print("✓ Cleared saved email")
            return True
        else:
            print("⚠ No email file to clear")
            return False
            
    except Exception as e:
        print(f"✗ Error clearing email: {e}")
        return False