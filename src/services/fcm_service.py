import os
import requests
from typing import Optional, Dict, List

try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("⚠ firebase-admin not installed")

class FCMService:
    def __init__(self, vercel_base_url: str = None, credentials_path: str = None):
        self.vercel_base_url = vercel_base_url or "https://lms-callback-git-main-astrallibertads-projects.vercel.app"
        self.fcm_enabled = False
        
        if not FIREBASE_AVAILABLE:
            print("⚠ Firebase Admin SDK not available")
            print("  Install: pip install firebase-admin")
            return
        
        if self._initialize_firebase(credentials_path):
            self.fcm_enabled = True
            print("✓ FCM Service initialized")
            print(f"  Vercel API: {self.vercel_base_url}")
    
    def _find_credentials_file(self, credentials_path: str = None) -> Optional[str]:
        possible_paths = []
        
        if credentials_path:
            possible_paths.append(credentials_path)
        
        possible_paths.extend([
            "firebase-admin-credentials.json",
            "services/firebase-admin-credentials.json",
            "src/services/firebase-admin-credentials.json",
        ])
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def _initialize_firebase(self, credentials_path: str = None) -> bool:
        if len(firebase_admin._apps) > 0:
            print("✓ Firebase Admin already initialized")
            return True
        
        creds_file = self._find_credentials_file(credentials_path)
        
        if not creds_file:
            print(f"⚠ Credentials file not found")
            print("  Download from Firebase Console → Service Accounts")
            return False
        
        try:
            cred = credentials.Certificate(creds_file)
            firebase_admin.initialize_app(cred)
            print(f"✓ Firebase Admin initialized with {creds_file}")
            return True
        except Exception as e:
            print(f"✗ Error initializing Firebase Admin: {e}")
            return False
    
    def _sanitize_email(self, email: str) -> str:
        return email.replace('.', '_').replace('@', '_')
    
    def get_token(self, email: str) -> Optional[str]:
        try:
            sanitized_email = self._sanitize_email(email)
            
            url = f"{self.vercel_base_url}/api/fcm/token/{sanitized_email}"
            
            print(f"Fetching token for {email}")
            print(f"  URL: {url}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    token = data.get('fcm_token')
                    if token:
                        print(f"✓ Token found for {email}: {token[:20]}...")
                        return token
                    else:
                        print(f"⚠ No token in response for {email}")
                else:
                    print(f"⚠ No token data found for {email}")
                    print(f"  User needs to login on Android app first")
            else:
                print(f"⚠ HTTP {response.status_code} from Vercel API")
        except Exception as e:
            print(f"✗ Error fetching token for {email}: {e}")
        
        return None
    
    def get_all_tokens(self) -> Dict[str, str]:
        """
        Get all FCM tokens via Vercel API
        """
        try:
            url = f"{self.vercel_base_url}/api/fcm/tokens"
            
            print(f"Fetching all tokens from Vercel API...")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    tokens = data.get('tokens', {})
                    print(f"✓ Found {len(tokens)} registered devices")
                    for email in tokens.keys():
                        print(f"  - {email}")
                    return tokens
                else:
                    print("⚠ No tokens registered yet")
            else:
                print(f"⚠ HTTP {response.status_code} from Vercel API")
        except Exception as e:
            print(f"✗ Error fetching all tokens: {e}")
        
        return {}
    
    def send_notification(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[Dict] = None,
        notification_type: str = "info"
    ) -> bool:
        if not self.fcm_enabled:
            print("⚠ FCM not enabled")
            return False
        
        try:
            data_payload = data or {}
            data_payload["notification_type"] = notification_type
            
            data_payload = {k: str(v) for k, v in data_payload.items()}
            
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data_payload,
                token=token,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        sound='default',
                        channel_id='lms_notifications',
                    )
                )
            )
            
            response = messaging.send(message)
            print(f"✓ FCM notification sent: {response}")
            return True
            
        except messaging.UnregisteredError:
            print(f"⚠ FCM token is invalid or unregistered")
            return False
        except Exception as e:
            print(f"✗ Error sending FCM notification: {e}")
            return False
    
    def send_to_user(
        self,
        email: str,
        title: str,
        body: str,
        data: Optional[Dict] = None,
        notification_type: str = "info"
    ) -> bool:
        token = self.get_token(email)
        if not token:
            print(f"⚠ No FCM token found for {email}")
            print(f"  User needs to login on Android app first")
            return False
        
        return self.send_notification(token, title, body, data, notification_type)
    
    def send_to_multiple(
        self,
        emails: List[str],
        title: str,
        body: str,
        data: Optional[Dict] = None,
        notification_type: str = "info"
    ) -> Dict[str, bool]:
        results = {}
        for email in emails:
            results[email] = self.send_to_user(email, title, body, data, notification_type)
        
        success_count = sum(1 for success in results.values() if success)
        print(f"✓ FCM notifications sent to {success_count}/{len(emails)} users")
        return results

_fcm_service = None

def get_fcm_service() -> FCMService:
    global _fcm_service
    if _fcm_service is None:
        _fcm_service = FCMService()
    return _fcm_service