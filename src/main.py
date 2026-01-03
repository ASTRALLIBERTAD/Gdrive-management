"""LMS Alternative - Main Application Module.

This module serves as the entry point for the Learning Management System (LMS)
Alternative application built with Flet. It handles application initialization,
OAuth configuration, authentication flow routing, and view management.

Functions:
    setup_paths: Configure Python path for module imports.
    repair_filesystem: Fix malformed filenames from Android file system.
    load_credentials: Load OAuth credentials from JSON file.
    get_redirect_url: Get the OAuth redirect URL for desktop authentication.
    main: Main application entry point and Flet page handler.

Example:
    Run the application directly::

        $ python main.py

    Or use Flet's app runner::

        >>> import flet as ft
        >>> ft.app(target=main)

See Also:
    :class:`~src.services.auth_service.GoogleAuth`: Authentication service.
    :class:`~src.ui.dashboard.Dashboard`: Main dashboard view.
    :class:`~src.ui.login.LoginView`: Desktop login view.
"""

import os
import sys
import json
import flet as ft

SCOPES = ["https://www.googleapis.com/auth/drive"]


def setup_paths():
    """Configure Python module import paths for application execution.

    Adds the application source directory and current working directory to
    Python's sys.path to enable proper module imports regardless of how the
    application is launched (direct execution, packaged, or from different
    working directories). Ensures project modules can be imported consistently.

    Purpose:
        - Enable module imports from application directory
        - Support execution from different working directories
        - Ensure consistent import behavior across platforms
        - Prepare environment for application initialization

    Returns:
        tuple: A 2-tuple containing path information:
            - app_path (str): Absolute path to the application source directory
              where main.py is located. Used for locating resource files.
            - cwd (str): Current working directory at application startup.
              Used for locating user data and configuration files.

    Algorithm:
        1. **Determine Application Path**:
           a. Get absolute path of current file (__file__)
           b. Extract directory path using os.path.dirname()
           c. Store in app_path variable
           d. This is the src directory containing main.py
        
        2. **Get Current Working Directory**:
           a. Call os.getcwd() to get current directory
           b. Store in cwd variable
           c. This is where user launched application
        
        3. **Update sys.path**:
           a. Create list: [cwd, app_path]
           b. For each path in list:
              i. Check if path already in sys.path
              ii. If not present:
                  - Call sys.path.insert(0, path)
                  - Adds to beginning of path (highest priority)
           c. Enables imports from both locations
        
        4. **Return Paths**:
           a. Return tuple (app_path, cwd)
           b. Caller can use paths for resource loading

    Interactions:
        - **os.path.abspath()**: Gets absolute file path
        - **os.path.dirname()**: Extracts directory from path
        - **os.getcwd()**: Gets current working directory
        - **sys.path.insert()**: Adds import paths to Python

    Example:
        >>> app_path, cwd = setup_paths()
        >>> print(f"Application directory: {app_path}")
        Application directory: /home/user/lms/src
        >>> print(f"Working directory: {cwd}")
        Working directory: /home/user/lms
        >>> 
        >>> # Now can import project modules
        >>> from services.auth_service import GoogleAuth
        >>> from ui.dashboard import Dashboard

    See Also:
        - :func:`main`: Calls this during initialization
        - :mod:`sys`: Python system module for path manipulation

    Notes:
        - Paths inserted at position 0 (highest priority)
        - Avoids duplicate entries in sys.path
        - Safe to call multiple times (idempotent)
        - app_path is where source code lives
        - cwd is where user launched application
        - Both paths may be same if launched from src directory
    """
    app_path = os.path.dirname(os.path.abspath(__file__))
    cwd = os.getcwd()
    
    for path in [cwd, app_path]:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    return app_path, cwd


def repair_filesystem(cwd):
    """Repair malformed filenames from Android file system issues.

    Fixes filenames containing backslashes that occur when files are created
    on Android's file system and then synced to other platforms. Android may
    create files with literal backslashes in names which appear as directory
    separators on other systems, causing path resolution failures.

    Purpose:
        - Fix Android file system compatibility issues
        - Repair backslash-containing filenames
        - Ensure proper directory structure
        - Enable cross-platform file access

    Args:
        cwd (str): Current working directory to scan for malformed filenames.
            Typically the directory where application data is stored. Only
            this directory is scanned (not recursive).

    Returns:
        None: Operates via side effects (renames files and creates directories).

    Algorithm:
        1. **Try File System Scan**:
           a. Enter outer try block for error handling
           b. Call os.listdir(cwd) to get list of files
           c. Store in files list
        
        2. **Process Each File**:
           a. For each filename in files list:
              i. Check if "\\" (backslash) in filename
              ii. If backslash not present, skip to next file
        
        3. **Repair Malformed Filename**:
           a. If backslash present:
              i. Replace "\\" with os.sep (platform separator)
                 - Windows: os.sep = "\\"
                 - Unix/Mac: os.sep = "/"
              ii. Store result in new_path variable
        
        4. **Create Missing Directories**:
           a. Extract directory from new_path using os.path.dirname()
           b. Store in dir_name variable
           c. If dir_name not empty and doesn't exist:
              i. Call os.makedirs(dir_name, exist_ok=True)
              ii. Creates all intermediate directories
        
        5. **Rename File**:
           a. Enter inner try block for rename operation
           b. Call os.rename(filename, new_path)
           c. Moves file to corrected path
           d. If OSError occurs:
              i. Pass silently (file may be locked or permission denied)
        
        6. **Handle All Errors**:
           a. Outer except catches any Exception
           b. Pass silently (don't interrupt app startup)
           c. Errors include: directory not accessible, permission issues

    Interactions:
        - **os.listdir()**: Lists files in directory
        - **os.path.dirname()**: Extracts directory from path
        - **os.path.exists()**: Checks directory existence
        - **os.makedirs()**: Creates directory hierarchy
        - **os.rename()**: Renames/moves file
        - **os.sep**: Platform-specific path separator

    Example:
        >>> # Android creates file: "data\\config.json"
        >>> # (backslash literally in filename)
        >>> repair_filesystem('/home/user/lms')
        >>> # After repair on Unix: "data/config.json"
        >>> # Directory "data" created, file moved to data/config.json
        >>> 
        >>> # Windows example: no change needed
        >>> # File: "data\\config.json" is already correct on Windows
        >>> repair_filesystem('C:\\Users\\User\\lms')
        >>> # os.sep = "\\" so replacement has no effect

    See Also:
        - :func:`main`: Calls this during initialization
        - :mod:`os.path`: Path manipulation utilities

    Notes:
        - Only processes top-level directory (not recursive)
        - Fails silently to avoid startup interruption
        - Android-specific issue but safe on all platforms
        - Creates intermediate directories as needed
        - Handles permission and lock errors gracefully
        - Only processes filenames with backslashes
        - Safe to call on directories without issues
    """
    try:
        files = os.listdir(cwd)
        for filename in files:
            if "\\" in filename:
                new_path = filename.replace("\\", os.sep)
                dir_name = os.path.dirname(new_path)
                if dir_name and not os.path.exists(dir_name):
                    os.makedirs(dir_name, exist_ok=True)
                try:
                    os.rename(filename, new_path)
                except OSError:
                    pass
    except Exception:
        pass

def find_files(search_dir, search_name):
    matches = []
    for root, dirs, files in os.walk(search_dir):
        for file in files:
            if search_name in file:
                matches.append(os.path.join(root, file))
    return matches

def load_credentials(app_path, cwd):

    """Load OAuth 2.0 credentials from JSON configuration file.

    Searches multiple locations for the OAuth credentials file (web.json),
    parses its contents, and extracts client ID, secret, and redirect URIs
    needed for Google OAuth authentication. Supports both 'web' and 'installed'
    application configurations.

    Purpose:
        - Locate OAuth credentials file in multiple locations
        - Parse JSON configuration safely
        - Extract OAuth client credentials
        - Support both web and installed app configs
        - Enable Google authentication initialization

    Args:
        app_path (str): Application source directory path. Typically the
            src directory where main.py is located. Used to search for
            credentials in services subdirectory.
        cwd (str): Current working directory. Where user launched application.
            Used to search for credentials in local services subdirectory.

    Returns:
        dict or None: Credentials dictionary if found, containing:
            - path (str): Absolute path to credentials file
            - client_id (str): OAuth 2.0 client ID from Google Console
            - client_secret (str): OAuth 2.0 client secret
            - redirect_uris (list): List of authorized redirect URIs
            Returns None if no valid credentials file found in any location.

    Algorithm:
        1. **Define Search Paths**:
           a. Create possible_paths list with 4 locations:
              i. app_path/services/web.json (deployed location)
              ii. cwd/services/web.json (local development)
              iii. app_path/web.json (root fallback)
              iv. cwd/web.json (local root fallback)
           b. Paths checked in order (first match wins)
        
        2. **Search Each Path**:
           a. For each creds_path in possible_paths:
              i. Check if file exists using os.path.exists()
              ii. If file doesn't exist, continue to next path
        
        3. **Try Loading File**:
           a. If file exists, enter try block
           b. Open file in read mode
           c. Parse JSON with json.load()
           d. Store in data variable
        
        4. **Extract Configuration**:
           a. Try to get 'web' section: data.get('web')
           b. If 'web' is None, try 'installed': data.get('installed')
           c. Store in config variable
           d. If config is None (neither section found), continue to next path
        
        5. **Build Credentials Dict**:
           a. If config found, create dictionary with:
              i. 'path': creds_path (file location)
              ii. 'client_id': config.get('client_id')
              iii. 'client_secret': config.get('client_secret')
              iv. 'redirect_uris': config.get('redirect_uris', [])
           b. Return credentials dictionary immediately
        
        6. **Handle Errors**:
           a. Catch any Exception during file read/parse
           b. Continue to next path (file may be malformed)
        
        7. **Return None** (if no valid file found):
           a. If all paths checked without success
           b. Return None to indicate failure

    Interactions:
        - **os.path.exists()**: Checks file existence
        - **os.path.join()**: Constructs file paths
        - **json.load()**: Parses JSON content
        - **File I/O**: Opens and reads credential file

    Example:
        >>> app_path = "/home/user/lms/src"
        >>> cwd = "/home/user/lms"
        >>> creds = load_credentials(app_path, cwd)
        >>> if creds:
        ...     print(f"Client ID: {creds['client_id']}")
        ...     print(f"Redirects: {creds['redirect_uris']}")
        ... else:
        ...     print("Credentials not found!")
        Client ID: 123456-abc.apps.googleusercontent.com
        Redirects: ['http://localhost:8550/oauth_callback']
        >>> 
        >>> # File not found scenario
        >>> creds = load_credentials("/invalid", "/paths")
        >>> print(creds)
        None

    See Also:
        - :func:`main`: Uses credentials for OAuth initialization
        - :class:`~services.auth_service.GoogleAuth`: Consumes credentials
        - :class:`~flet.auth.providers.GoogleOAuthProvider`: Uses client ID/secret

    Notes:
        - Searches 4 locations in priority order
        - Supports both 'web' and 'installed' app types
        - First valid file found is used (no merging)
        - Returns None if no valid file found (caller must handle)
        - Malformed JSON files skipped silently
        - redirect_uris defaults to empty list if missing
        - File must be named exactly "web.json"
        - OAuth credentials from Google Cloud Console
    """

    filenames = ["web.json", "credentials.json"]
    possible_paths = []
    
    for filename in filenames:
        possible_paths.extend([
            os.path.join(app_path, "services", filename),
            os.path.join(cwd, "services", filename),
            os.path.join(app_path, filename),
            os.path.join(cwd, filename)
        ])
    
    for creds_path in possible_paths:
        if os.path.exists(creds_path):
            try:
                with open(creds_path, 'r') as f:
                    data = json.load(f)
                    config = data.get('web') or data.get('installed')
                    
                    if not config:
                        continue
                    
                    return {
                        'path': creds_path,
                        'client_id': config.get('client_id'),
                        'client_secret': config.get('client_secret'),
                        'redirect_uris': config.get('redirect_uris', [])
                    }
            except Exception:
                continue
    
    return None


def get_redirect_url():
    """Get the OAuth 2.0 redirect URL for desktop authentication.

    Returns the localhost callback URL used for OAuth authentication on
    desktop platforms. This URL must match the authorized redirect URIs
    configured in Google Cloud Console for the OAuth client.

    Returns:
        str: The localhost redirect URL with port 8550. Format:
            "http://localhost:8550/oauth_callback". Port 8550 chosen to
            avoid conflicts with common services.

    Algorithm:
        1. **Return Static URL**:
           a. Return hardcoded string: "http://localhost:8550/oauth_callback"
           b. No computation or configuration needed
           c. Must match Google Console settings

    Interactions:
        - **GoogleOAuthProvider**: Uses this URL for OAuth configuration

    Example:
        >>> url = get_redirect_url()
        >>> print(url)
        http://localhost:8550/oauth_callback
        >>> 
        >>> # Used in OAuth provider setup
        >>> provider = GoogleOAuthProvider(
        ...     client_id=client_id,
        ...     redirect_url=get_redirect_url()
        ... )

    See Also:
        - :meth:`main`: Uses this for OAuth provider configuration
        - :class:`~services.auth_service.GoogleAuth`: Implements OAuth flow
        - :class:`~flet.auth.providers.GoogleOAuthProvider`: OAuth provider

    Notes:
        - Port 8550 chosen to avoid common conflicts
        - Must be authorized in Google Cloud Console
        - Desktop authentication only (not mobile)
        - Local HTTP server listens on this port during auth
        - URL format must be exact: `http://localhost:{PORT}/{PATH}`
        - No HTTPS for localhost (not required by Google)
    """
    return "http://localhost:8550/oauth_callback"


def main(page: ft.Page):
    """Main application entry point and Flet page handler.

    Initializes and manages the entire LMS application lifecycle including
    OAuth configuration, authentication state management, and view routing.
    Handles both desktop and mobile platforms with appropriate login flows
    and provides comprehensive error handling for initialization failures.

    Purpose:
        - Initialize Flet application and page configuration
        - Setup OAuth authentication services
        - Manage authentication state and routing
        - Handle platform-specific login flows (desktop vs mobile)
        - Provide dashboard access for authenticated users
        - Handle logout and re-authentication

    Args:
        page (ft.Page): Flet page instance provided by the Flet runtime.
            Represents the application window/screen and provides access
            to UI controls, platform detection, and event handling. Modified
            throughout function to display different views.

    Returns:
        None: Function operates via side effects on page object. Controls
            application lifecycle until user exits.

    Raises:
        Exception: Critical errors during initialization displayed on page
            with error message and stack trace. Application continues running
            in error state to allow debugging.

    Algorithm:
        **Phase 1: Page Configuration**
            1. Set page.title = "LMS Alternative"
            2. Set page.theme_mode = LIGHT
            3. Set page.bgcolor = WHITE
            4. Set page.padding = 0 (full-screen layout)
        
        **Phase 2: Environment Setup**
            1. Call setup_paths() to configure imports
            2. Store returned app_path and cwd
            3. Call repair_filesystem(cwd) to fix Android issues
        
        **Phase 3: Module Imports**
            1. Import GoogleAuth from services.auth_service
            2. Import Dashboard from ui.dashboard
            3. Import LoginView from ui.login
            4. Try to import FirebaseMobileLogin:
               a. If ImportError, set to None (not available)
        
        **Phase 4: Credentials Loading**
            1. Call load_credentials(app_path, cwd)
            2. If creds is None:
               a. Display error: "ERROR: web.json not found!"
               b. Return early (cannot proceed without credentials)
        
        **Phase 5: OAuth Provider Setup**
            1. Get redirect URL via get_redirect_url()
            2. Create GoogleAuth service with credentials file
            3. Create GoogleOAuthProvider with:
               a. client_id from credentials
               b. client_secret from credentials
               c. redirect_url from get_redirect_url()
            4. Set provider.scopes = ["openid", "email", "profile"]
        
        **Phase 6: Define Handler Functions**
            
            **handle_on_login(e)** - OAuth callback handler:
                1. Check if e.error exists (auth failed)
                2. If error, show snackbar and return
                3. Verify page.auth.token exists
                4. If no token, show error and return
                5. Extract token_data from page.auth.token
                6. If dict, add client_id and client_secret
                7. Call auth_service.login_with_token(token_data)
                8. If successful, show_dashboard()
                9. If failed, show error snackbar
            
            **show_snackbar(message)** - Display notification:
                1. Create SnackBar with message
                2. Set action to "Dismiss"
                3. Set open = True
                4. Call page.update()
            
            **show_dashboard()** - Display main application:
                1. Clear page.controls
                2. Create Dashboard instance with:
                   a. page reference
                   b. auth_service
                   c. handle_logout callback
                3. Get dashboard view via get_view()
                4. Add to page
                5. Call page.update()
            
            **handle_logout()** - Process user logout:
                1. Call auth_service.logout() to clear credentials
                2. If page.auth has logout method, call it
                3. Call show_login() to return to login screen
            
            **show_login()** - Display login view:
                1. Clear page.controls
                2. Detect platform: is_mobile = platform in [ANDROID, IOS]
                3. If mobile and FirebaseMobileLogin available:
                   a. Load firebase_config.json if exists
                   b. Create FirebaseMobileLogin with config
                   c. Add to page
                4. Else (desktop):
                   a. Create LoginView with provider
                   b. Add to page
                5. Call page.update()
        
        **Phase 7: Register OAuth Callback**
            1. Set page.on_login = handle_on_login
            2. Flet calls this when OAuth completes
        
        **Phase 8: Initial Route**
            1. Check if auth_service.is_authenticated()
            2. If True: call show_dashboard()
            3. If False: call show_login()
        
        **Phase 9: Error Handling**
            1. Outer try-except catches all initialization errors
            2. On exception:
               a. Import traceback
               b. Format full stack trace
               c. Display error message on page (red text)
               d. Print full traceback to console
               e. Application remains in error state

    Interactions:
        - **setup_paths()**: Configures import paths
        - **repair_filesystem()**: Fixes Android file issues
        - **load_credentials()**: Loads OAuth configuration
        - **get_redirect_url()**: Gets OAuth redirect URL
        - **GoogleAuth**: Manages authentication state
        - **GoogleOAuthProvider**: Configures OAuth flow
        - **Dashboard**: Main application view (authenticated)
        - **LoginView**: Desktop login view
        - **FirebaseMobileLogin**: Mobile login view (optional)
        - **ft.Page**: Application window/screen management

    Example:
        >>> # Flet automatically calls main with page instance
        >>> import flet as ft
        >>> ft.app(target=main)
        >>> 
        >>> # Application flow:
        >>> # 1. main(page) called by Flet
        >>> # 2. Page configured and OAuth setup
        >>> # 3. Check authentication state
        >>> # 4a. If authenticated -> Dashboard shown
        >>> # 4b. If not authenticated -> Login shown
        >>> # 5. User logs in -> OAuth callback -> Dashboard
        >>> # 6. User clicks logout -> Login shown again

    See Also:
        - :func:`setup_paths`: Configures module imports
        - :func:`load_credentials`: Loads OAuth config
        - :func:`repair_filesystem`: Fixes Android issues
        - :class:`~services.auth_service.GoogleAuth`: Authentication service
        - :class:`~ui.dashboard.Dashboard`: Main application view
        - :class:`~ui.login.LoginView`: Desktop login
        - :class:`~ui.firebase_mobile_login.FirebaseMobileLogin`: Mobile login
        - :class:`~flet.auth.providers.GoogleOAuthProvider`: OAuth provider

    Notes:
        - Entry point for entire application
        - Handles both desktop (Windows, macOS, Linux) and mobile (Android, iOS)
        - OAuth scopes: openid, email, profile (basic user info)
        - FirebaseMobileLogin optional (gracefully degrades if not available)
        - Nested functions access outer scope variables (closures)
        - Critical errors displayed on page (doesn't crash silently)
        - Authentication state checked on startup
        - Page cleared between view transitions
        - Dashboard requires authentication (checks on entry)
        - Logout returns to login screen (clears session)
    """
    page.title = "LMS Alternative"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.WHITE
    page.padding = 0
    
    try:
        app_path, cwd = setup_paths()
        repair_filesystem(cwd)
        
        from services.auth_service import GoogleAuth
        from ui.dashboard import Dashboard
        from ui.login import LoginView
        from ui.custom_control.multi_account_manager import MultiAccountManager
        from utils.common import show_snackbar
        from services.fcm_integration import register_fcm_for_user

        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        file_to_find = "fcm_email.txt"


        found_files = find_files(parent_dir, file_to_find)
        if found_files:
            show_snackbar(page, "Files found:", ft.Colors.GREEN, duration=9)
            print("Files found:")
            for f in found_files:
                print(f)
                show_snackbar(page, f, ft.Colors.GREEN, duration=9)
        else:
            show_snackbar(page, "No files found.", ft.Colors.RED, duration=9)
            print("No files found.")
        
        try:
            from ui.firebase_mobile_login import FirebaseMobileLogin
        except ImportError:
            FirebaseMobileLogin = None
        
        creds = load_credentials(app_path, cwd)
        if not creds:
            page.add(ft.Text("ERROR: web.json not found!", color=ft.Colors.RED))
            page.update()
            return

        redirect_url = get_redirect_url()
        auth_service = GoogleAuth(credentials_file=creds['path'])
        account_manager = MultiAccountManager()
        
        from flet.auth.providers import GoogleOAuthProvider
        
        provider = GoogleOAuthProvider(
            client_id=creds['client_id'],
            client_secret=creds['client_secret'],
            redirect_url=redirect_url
        )
        provider.scopes = ["openid", "email", "profile"]
        
        def save_current_account_if_logged_in():
            if auth_service.is_authenticated() and auth_service.creds:
                user_info = auth_service.get_user_info()
                if user_info:
                    email = user_info.get("emailAddress")
                    if email:
                        token_dict = {
                            'token': auth_service.creds.token,
                            'refresh_token': auth_service.creds.refresh_token,
                            'token_uri': auth_service.creds.token_uri,
                            'client_id': auth_service.creds.client_id,
                            'client_secret': auth_service.creds.client_secret,
                            'scopes': list(auth_service.creds.scopes) if auth_service.creds.scopes else SCOPES,
                        }
                        account_manager.add_account(email, user_info, token_dict, save_credentials=True)
                        print(f"✓ Account saved: {email}")
                        return email
            return None
        
        def handle_on_login(e):
            if e.error:
                show_snackbar(page, f"Login Error: {e.error}", ft.Colors.RED)
                return
            
            if not hasattr(page.auth, 'token') or not page.auth.token:
                show_snackbar(page, "Authentication failed: No token received", ft.Colors.RED)
                return
            
            token_data = page.auth.token
            
            if isinstance(token_data, dict):
                token_data['client_id'] = creds['client_id']
                token_data['client_secret'] = creds['client_secret']
            
            if auth_service.login_with_token(token_data):
                save_current_account_if_logged_in()
                user_info = auth_service.get_user_info()
                if user_info:
                    email = user_info.get("emailAddress")
                    account_manager.set_current_account(email)

                    register_fcm_for_user(page, email)
                show_dashboard()
            else:
                show_snackbar(page, "Authentication failed: Could not complete login", ft.Colors.RED)

        
        page.on_login = handle_on_login
                
        def show_dashboard():
            page.controls.clear()
            dashboard = Dashboard(
                page, 
                auth_service, 
                handle_logout,
                on_add_account=handle_add_account,
                on_switch_account=handle_switch_account
            )
            page.add(dashboard.get_view() if hasattr(dashboard, 'get_view') else dashboard)
            page.update()
        
        def handle_logout():
            auth_service.logout()
            if hasattr(page.auth, 'logout'):
                page.auth.logout()
            
            from services.fcm_integration import clear_saved_email
            clear_saved_email(page)
            
            show_login()
        
        def handle_add_account():
            save_current_account_if_logged_in()
            
            if hasattr(page.auth, 'logout'):
                page.auth.logout()
            
            show_login(is_adding_account=True)
        
        def handle_switch_account(email):
            save_current_account_if_logged_in()
            
            account_data = account_manager.get_account(email)
            if not account_data:
                show_snackbar(page, f"Account {email} not found.", ft.Colors.RED)
                return
            
            token_data = account_data.get("token_data")
            if token_data:
                if auth_service.login_with_token(token_data):
                    account_manager.set_current_account(email)
                    register_fcm_for_user(page, email)
                    show_dashboard()
                else:
                    show_snackbar(page, f"Session expired for {email}. Please login again.", ft.Colors.ORANGE)
                    if hasattr(page.auth, 'logout'):
                        page.auth.logout()
                    show_login(switching_to_email=email)
            else:
                if hasattr(page.auth, 'logout'):
                    page.auth.logout()
                show_login(switching_to_email=email)
        
        def show_login(is_adding_account=False, switching_to_email=None):
            page.controls.clear()
            
            is_mobile = page.platform in [ft.PagePlatform.ANDROID, ft.PagePlatform.IOS]
            
            if switching_to_email:
                info_text = ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=48, color=ft.Colors.BLUE),
                        ft.Text(
                            f"Please login to {switching_to_email}",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "This account requires re-authentication",
                            size=14,
                            color=ft.Colors.GREY_700,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                )
                page.add(info_text)
            elif is_adding_account:
                info_text = ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Icon(ft.Icons.PERSON_ADD, size=48, color=ft.Colors.GREEN),
                        ft.Text(
                            "Add Another Account",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "Your current account will remain saved",
                            size=14,
                            color=ft.Colors.GREY_700,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                )
                page.add(info_text)
            
            if is_mobile and FirebaseMobileLogin:
                firebase_config_path = os.path.join(app_path, "services", "firebase_config.json")
                if not os.path.exists(firebase_config_path):
                    firebase_config_path = os.path.join(cwd, "services", "firebase_config.json")
                
                firebase_config = {}
                if os.path.exists(firebase_config_path):
                    with open(firebase_config_path, 'r') as f:
                        firebase_config = json.load(f)
                
                page.add(FirebaseMobileLogin(
                    page, 
                    auth_service, 
                    firebase_config,
                    creds['client_id'],
                    on_success=show_dashboard
                ))
            else:
                login_view = LoginView(page, provider, auth_service, on_success=show_dashboard)
                page.add(login_view)
            
            page.update()
        
        if auth_service.is_authenticated():
            current_email = save_current_account_if_logged_in()
            if current_email:
                account_manager.set_current_account(current_email)
                # Re-register FCM on Android app restart
                register_fcm_for_user(page, current_email)
            show_dashboard()
        else:
            show_login()
            
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        page.add(ft.Text(f"CRITICAL ERROR: {e}", color=ft.Colors.RED))
        page.update()
        print(f"CRITICAL ERROR:\n{error_msg}")

if __name__ == "__main__":
    ft.app(target=main)
