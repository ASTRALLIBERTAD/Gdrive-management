import os
import pickle
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


class BaseAuthService:
    def __init__(self, credentials_file, token_file, scopes):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.scopes = scopes
        self.creds = None
        self.client_id = None
        self.client_secret = None
    
    def _load_client_info(self):
        if not os.path.exists(self.credentials_file):
            return False
        
        try:
            with open(self.credentials_file, 'r') as f:
                data = json.load(f)
                config = data.get('web') or data.get('installed')
                if config:
                    self.client_id = config.get('client_id')
                    self.client_secret = config.get('client_secret')
                    return True
        except Exception as e:
            print(f"Error loading client info: {e}")
        return False
    
    def _load_credentials(self):
        if not os.path.exists(self.token_file):
            return False
        
        try:
            with open(self.token_file, 'rb') as token:
                self.creds = pickle.load(token)
            return True
        except Exception as e:
            print(f"Error loading token: {e}")
            self.creds = None
        return False
    
    def _save_credentials(self):
        try:
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.creds, token)
            return True
        except Exception as e:
            print(f"Error saving token: {e}")
        return False
    
    def _refresh_credentials(self):
        if not self.creds or not self.creds.refresh_token:
            return False
        
        try:
            self.creds.refresh(Request())
            self._save_credentials()
            return True
        except Exception as e:
            print(f"Error refreshing token: {e}")
        return False
    
    def is_authenticated(self):
        if not self.creds:
            return False
        
        if not self.creds.expired:
            return self.creds.valid
        
        return self._refresh_credentials()
    
    def logout(self):
        self.creds = None
        if os.path.exists(self.token_file):
            try:
                os.remove(self.token_file)
            except Exception as e:
                print(f"Error removing token file: {e}")


class TokenManager:
    @staticmethod
    def create_credentials_from_token(token_data, client_id, client_secret, scopes):
        access_token = token_data.get("access_token")
        if not access_token:
            return None
        
        refresh_token = token_data.get("refresh_token")
        scope = token_data.get("scope", scopes)
        if isinstance(scope, str):
            scope = scope.split() if scope else scopes
        
        return Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=scope
        )
    
    @staticmethod
    def validate_and_refresh(creds):
        if creds.valid:
            return True, None
        
        if not creds.expired or not creds.refresh_token:
            return False, "Credentials not valid and cannot be refreshed"
        
        try:
            creds.refresh(Request())
            return True, None
        except Exception as e:
            return False, str(e)