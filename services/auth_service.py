import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive"]

class GoogleAuth:
    def __init__(self, credentials_file=None):
        self.creds = None
        self.credentials_file = credentials_file or os.path.join(os.path.dirname(__file__), "client_secret_884285758192-svsp3rvcku729i3p17nibs2475bshmgv.apps.googleusercontent.com.json")

    def login(self):
        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(f"credentials.json not found at {self.credentials_file}")
        flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
        # Automatically opens browser, works cross-platform
        self.creds = flow.run_local_server(port=0)

    def is_authenticated(self):
        return self.creds is not None
