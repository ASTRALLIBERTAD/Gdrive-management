import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from utils.auth_base import BaseAuthService, TokenManager

SCOPES = ["https://www.googleapis.com/auth/drive"]


class GoogleAuth(BaseAuthService):
    def __init__(self, credentials_file=None):
        super().__init__(
            credentials_file=credentials_file or os.path.join(os.path.dirname(__file__), "web.json"),
            token_file=os.path.join(os.path.dirname(__file__), "token.pickle"),
            scopes=SCOPES
        )
        self._load_client_info()
        self._load_credentials()
        if self.client_id:
            print(f"✓ Loaded client info from {os.path.basename(self.credentials_file)}")
        if self.creds:
            print("✓ Loaded existing credentials from token.pickle")

    def login_desktop(self):
        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(f"Credentials file not found at {self.credentials_file}")
        
        print("Starting desktop OAuth flow...")
        flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
        self.creds = flow.run_local_server(port=8550)
        self._save_credentials()
        print("✓ Desktop login successful")

    def login_with_token(self, token_data):
        try:
            print("Bridging OAuth token to Google credentials")
            print(f"Token data type: {type(token_data)}")
            
            if not isinstance(token_data, dict):
                print("Token data is not a dictionary")
                return False
            
            access_token = token_data.get("access_token")
            if not access_token:
                print("No access_token in token_data")
                return False
            
            client_id = token_data.get("client_id") or self.client_id
            client_secret = token_data.get("client_secret") or self.client_secret
            
            self._log_token_status(token_data, client_id, client_secret)
            
            self.creds = TokenManager.create_credentials_from_token(
                token_data, client_id, client_secret, SCOPES
            )
            
            if not self.creds:
                print("Failed to create credentials from token")
                return False
            
            is_valid, error = TokenManager.validate_and_refresh(self.creds)
            if not is_valid:
                print(f"Credentials validation failed: {error}")
                return False
            
            print("Credentials are valid")
            self._save_credentials()
            return True
            
        except Exception as e:
            import traceback
            print(f"Error bridging token: {e}")
            print(f"Traceback:\n{traceback.format_exc()}")
            return False

    def _log_token_status(self, token_data, client_id, client_secret):
        print(f"Access token: present")
        print(f"Refresh token: {'present' if token_data.get('refresh_token') else 'missing'}")
        print(f"Client ID: {'present' if client_id else 'missing'}")
        print(f"Client secret: {'present' if client_secret else 'missing'}")
        scope = token_data.get("scope", SCOPES)
        print(f"Scopes: {', '.join(scope) if isinstance(scope, list) else scope}")

    def get_service(self):
        if not self.is_authenticated():
            print("Cannot get service - not authenticated")
            return None
        
        try:
            service = build('drive', 'v3', credentials=self.creds)
            print("Google Drive service created")
            return service
        except Exception as e:
            print(f"Error creating service: {e}")
            return None

    def get_user_info(self):
        try:
            service = self.get_service()
            if not service:
                return {}
            about = service.about().get(fields="user").execute()
            user = about.get('user', {})
            email = user.get('emailAddress', 'unknown')
            print(f"✓ User info retrieved: {email}")
            return user
        except Exception as e:
            print(f"Error getting user info: {e}")
            return {}