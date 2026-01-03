"""Firebase Mobile Login Module.

This module provides a mobile-friendly OAuth authentication UI component
for the Learning Management System. It handles Google OAuth 2.0 authentication
on mobile platforms where native OAuth popups are unavailable.

Classes:
    FirebaseMobileLogin: A Flet Column component for mobile Google OAuth login.

Example:
    >>> login_view = FirebaseMobileLogin(
    ...     page=page,
    ...     auth_service=auth,
    ...     firebase_config=config,
    ...     oauth_client_id="client_id",
    ...     on_success=lambda: page.go("/dashboard")
    ... )
    >>> page.add(login_view)
"""

import flet as ft
import urllib.parse
import urllib.request
import urllib.error
import json
import secrets
import threading


class FirebaseMobileLogin(ft.Column):
    """Mobile-friendly OAuth 2.0 authentication component for Google sign-in.

    FirebaseMobileLogin is a specialized Flet UI component that provides a complete
    mobile authentication workflow for the Learning Management System. It addresses
    the limitation of mobile platforms where native OAuth popup windows are unavailable
    by launching an external browser for authentication, then polling a callback server
    to retrieve the OAuth tokens once the user completes sign-in.
    
    This component implements a secure OAuth 2.0 implicit grant flow with state
    parameter validation, background polling for token retrieval, and comprehensive
    error handling. It integrates seamlessly with the application's authentication
    service and provides real-time status updates throughout the login process.

    Purpose:
        - Provide mobile-compatible Google OAuth 2.0 authentication interface
        - Launch external browser for user sign-in on mobile platforms
        - Poll callback server to retrieve OAuth tokens after authentication
        - Handle authentication flow with progress indicators and status updates
        - Integrate with application's authentication service for token management
        - Support platform detection and responsive UI for various mobile devices

    Attributes:
        page (ft.Page): Flet page instance providing UI rendering, updates, and
            platform detection. Used for launching external URLs and running
            async UI update tasks.
        auth (GoogleAuth): Authentication service managing OAuth token storage,
            credential validation, and Drive API service initialization. Provides
            login_with_token() method for token processing.
        firebase_config (dict): Firebase project configuration containing API keys,
            project ID, auth domain, and other Firebase-specific settings. Used
            for Firebase integration if needed (currently OAuth-focused).
        oauth_client_id (str): Google OAuth 2.0 client ID for authentication
            requests. Must match the client ID configured in Google Cloud Console
            with authorized redirect URIs.
        on_success (Callable or None): Optional callback function with no parameters,
            invoked after successful authentication. Typically navigates to dashboard
            or main application view. Signature: () -> None.
        session_id (str or None): Unique session identifier generated using
            secrets.token_urlsafe(16). Used as OAuth state parameter for CSRF
            protection and callback server token retrieval. None before login initiated.
        polling (bool): Flag indicating whether background token polling thread is
            active. Set to True when polling starts, False when tokens received or
            timeout occurs. Controls polling loop continuation.
        status_text (ft.Text): UI text element displaying current authentication
            status messages to user. Color changes to indicate progress, success,
            or errors. Updated throughout login flow.
        login_button (ft.ElevatedButton): Primary action button for initiating
            Google sign-in. Disabled during authentication process, re-enabled
            on timeout or error.
        progress (ft.ProgressRing): Circular progress indicator shown during
            authentication. Visible while waiting for user to complete sign-in
            and during token processing. Hidden when idle or complete.

    Interactions:
        - **GoogleAuth**: Calls login_with_token() to process OAuth credentials
        - **ft.Page**: Uses launch_url() to open browser, run_task() for async updates
        - **Callback Server**: Polls HTTPS endpoint for token retrieval via urllib
        - **Google OAuth**: External browser navigates to accounts.google.com for auth
        - **secrets module**: Generates cryptographically secure session IDs
        - **threading module**: Runs background polling in daemon thread
        - **urllib**: Makes HTTP requests to callback server for token checking
        - **json module**: Parses JSON responses from callback server

    Algorithm (High-Level Workflow):
        **Phase 1: Initialization**
            1. Call parent ft.Column constructor with layout settings
            2. Store references to page, auth service, firebase config, client ID
            3. Initialize session_id to None and polling flag to False
            4. Initialize UI component references (status_text, login_button, progress)
            5. Call _build_ui() to construct and arrange interface elements
        
        **Phase 2: UI Construction** (_build_ui)
            1. Detect platform name for display (Android, iOS, etc.)
            2. Add header components (icon, title, subtitle)
            3. Create status text element for progress messages
            4. Create login button with Google branding and styling
            5. Create progress ring (initially hidden)
            6. Append all components to self.controls list
        
        **Phase 3: Login Initiation** (handle_login)
            1. Generate unique session_id using secrets.token_urlsafe(16)
            2. Update status to "Opening browser..." (orange color)
            3. Disable login button and show progress indicator
            4. Construct OAuth URL with client ID, scopes, and session_id as state
            5. Launch external browser with OAuth URL via page.launch_url()
            6. Update status to "Waiting for sign-in..." (blue color)
            7. Start background polling thread via _start_polling()
        
        **Phase 4: Background Token Polling** (_start_polling)
            1. Set polling flag to True
            2. Create daemon thread for polling loop
            3. Start thread to run in background (non-blocking)
            4. Polling loop (in thread):
               a. Maximum 60 attempts, 5-second intervals (5 minutes total)
               b. For each attempt:
                  - Update waiting status with animated dots
                  - Send GET request to callback server with session_id
                  - Parse JSON response for token data
                  - If access_token found: call _handle_tokens() and exit loop
                  - If HTTP error or no token: wait 5 seconds, retry
               c. If max attempts reached without token: call _handle_timeout()
        
        **Phase 5: Token Processing** (_handle_tokens)
            1. Stop polling by setting flag to False
            2. Update status to "Authenticating..." (green color)
            3. Construct token_data dictionary with access_token and metadata
            4. Call auth.login_with_token(token_data) to process credentials
            5. If authentication successful:
               a. Update status to "Authentication complete!" (green)
               b. Hide progress indicator
               c. Invoke on_success() callback if provided
            6. If authentication failed:
               a. Update status to "Authentication failed" (red)
               b. Re-enable login button for retry
               c. Hide progress indicator
        
        **Phase 6: Timeout Handling** (_handle_timeout)
            1. Stop polling by setting flag to False
            2. Update status to "Timeout - Sign-in took too long" (orange)
            3. Re-enable login button to allow retry
            4. Hide progress indicator
            5. User can click login button to start new session

    Example:
        >>> # Setup configuration
        >>> firebase_config = {
        ...     'apiKey': 'AIza...',
        ...     'projectId': 'my-project'
        ... }
        >>> oauth_client_id = '123456-abc.apps.googleusercontent.com'
        >>> 
        >>> # Define success handler
        >>> def on_login_success():
        ...     page.go('/dashboard')
        ...     print('Login successful!')
        >>> 
        >>> # Create login component
        >>> login = FirebaseMobileLogin(
        ...     page=page,
        ...     auth_service=auth,
        ...     firebase_config=firebase_config,
        ...     oauth_client_id=oauth_client_id,
        ...     on_success=on_login_success
        ... )
        >>> 
        >>> # Add to page
        >>> page.add(login)
        >>> page.update()
        >>> 
        >>> # User clicks "Sign in with Google" button
        >>> # 1. Browser opens to Google sign-in page
        >>> # 2. User authenticates with Google account
        >>> # 3. Callback server receives OAuth token
        >>> # 4. Polling loop retrieves token
        >>> # 5. auth.login_with_token() processes credentials
        >>> # 6. on_login_success() called -> navigates to dashboard

    See Also:
        - :class:`~src.services.google_auth.GoogleAuth`: Authentication service
        - :class:`~src.ui.login.LoginView`: Desktop OAuth login implementation
        - :mod:`secrets`: Cryptographic random number generation
        - :mod:`threading`: Thread-based parallelism for background polling
        - `Google OAuth 2.0 <https://developers.google.com/identity/protocols/oauth2>`_

    Notes:
        - Uses OAuth 2.0 implicit grant flow (response_type=token)
        - Tokens returned in URL fragment, not query string
        - Callback server temporarily stores tokens indexed by session_id
        - Polling runs for maximum 5 minutes (60 x 5 seconds)
        - State parameter (session_id) provides CSRF protection
        - External browser required on mobile (no popup support)
        - Progress indicator shows active authentication process
        - Login button disabled during authentication to prevent double-click
        - All UI updates run on main thread via page.run_task()
        - Polling thread is daemon thread (exits when app closes)

    Security Considerations:
        - session_id provides CSRF protection via OAuth state parameter
        - Tokens retrieved over HTTPS from callback server
        - Access tokens have limited lifetime (expires_in)
        - Client secret managed by auth service, not exposed in UI
        - Callback server should validate redirect URIs

    References:
        - OAuth 2.0 Implicit Grant: https://oauth.net/2/grant-types/implicit/
        - Flet Documentation: https://flet.dev/docs/
        - Google OAuth Scopes: https://developers.google.com/identity/protocols/oauth2/scopes
    """

    def __init__(self, page, auth_service, firebase_config, oauth_client_id, on_success=None):
        """Initialize the FirebaseMobileLogin component with configuration and callbacks.

        Constructs the mobile OAuth login interface by setting up references to
        required services, initializing state variables, and building the UI
        component tree. Prepares the component for rendering and user interaction.

        Args:
            page (ft.Page): Flet page instance for UI updates, platform detection,
                and URL launching. Must be initialized and active. Provides access
                to page.platform (device type) and page.launch_url() (browser).
            auth_service (GoogleAuth): Authentication service for OAuth token
                processing and credential management. Must provide login_with_token()
                method and client_secret attribute.
            firebase_config (dict): Firebase project configuration dictionary
                containing keys like 'apiKey', 'projectId', 'authDomain'. Used
                for potential Firebase integration. Required parameter but
                currently OAuth-focused implementation.
            oauth_client_id (str): Google OAuth 2.0 client ID string from Google
                Cloud Console. Must be authorized with callback redirect URI.
                Format: '123456-abc.apps.googleusercontent.com'
            on_success (Callable, optional): Callback function invoked after
                successful authentication. Should handle navigation to main app
                view. Signature: () -> None. Defaults to None (no action).

        Algorithm:
            1. **Initialize Parent Column**:
               a. Call super().__init__() with layout configuration
               b. Set controls to empty list (populated by _build_ui)
               c. Set alignment to MainAxisAlignment.CENTER (vertical centering)
               d. Set horizontal_alignment to CrossAxisAlignment.CENTER
               e. Set expand=True to fill available space
               f. Set spacing=20 between child components
            
            2. **Store Service References**:
               a. Assign page parameter to self.page
               b. Assign auth_service to self.auth
               c. Assign firebase_config to self.firebase_config
               d. Assign oauth_client_id to self.oauth_client_id
               e. Assign on_success callback to self.on_success
            
            3. **Initialize Session State**:
               a. Set self.session_id to None (no active session yet)
               b. Set self.polling to False (no background polling active)
            
            4. **Initialize UI Component References**:
               a. Set self.status_text to None (created in _build_ui)
               b. Set self.login_button to None (created in _build_ui)
               c. Set self.progress to None (created in _build_ui)
            
            5. **Build User Interface**:
               a. Call self._build_ui()
               b. Constructs all UI components
               c. Populates self.controls with component tree
               d. Stores references to key components for later updates
               e. Component now ready for rendering

        Interactions:
            - **ft.Column**: Parent class constructor for layout configuration
            - **_build_ui()**: Called to construct UI component tree

        Example:
            >>> # Create with minimal configuration
            >>> login = FirebaseMobileLogin(
            ...     page=page,
            ...     auth_service=auth,
            ...     firebase_config={'apiKey': 'key123'},
            ...     oauth_client_id='client_id',
            ...     on_success=None
            ... )
            >>> print(f"Session ID: {login.session_id}")
            Session ID: None
            >>> print(f"Polling active: {login.polling}")
            Polling active: False
            >>> 
            >>> # Create with success callback
            >>> def navigate_to_dashboard():
            ...     page.go('/dashboard')
            >>> 
            >>> login_with_callback = FirebaseMobileLogin(
            ...     page=page,
            ...     auth_service=auth,
            ...     firebase_config=config,
            ...     oauth_client_id='client_id',
            ...     on_success=navigate_to_dashboard
            ... )

        See Also:
            - :meth:`_build_ui`: Constructs the UI component tree
            - :class:`~src.services.google_auth.GoogleAuth`: Auth service requirements
            - :class:`ft.Column`: Parent Flet column container

        Notes:
            - Component is a Flet Column, can be added directly to page
            - UI components created in _build_ui, not in __init__
            - Session state initialized to inactive (no polling, no session)
            - on_success callback is optional (None check before invocation)
            - All parameters except on_success are required
            - Component ready for rendering immediately after initialization
        """
        super().__init__(
            controls=[],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
            spacing=20
        )
        self.page = page
        self.auth = auth_service
        self.firebase_config = firebase_config
        self.oauth_client_id = oauth_client_id
        self.on_success = on_success
        self.session_id = None
        self.polling = False
        
        self.status_text = None
        self.login_button = None
        self.progress = None
        
        self._build_ui()
        
    def _build_ui(self):
        """Construct and arrange all login interface UI components.

        Builds the complete user interface by creating and configuring all UI
        elements including header, status text, login button, and progress
        indicator. Arranges components in a centered, vertically-stacked layout.

        Returns:
            None: Modifies self.controls list in place with UI components.
                Also stores references to interactive elements in instance
                attributes (status_text, login_button, progress).

        Algorithm:
            1. **Detect Platform**:
               a. Call _get_platform_name() to get human-readable platform name
               b. Store result in platform_name variable
               c. Used for display text (e.g., "Platform: Android")
            
            2. **Add Header Components**:
               a. Add 50px vertical spacing Container at top
               b. Add cloud icon (ft.Icons.CLOUD_CIRCLE):
                  - Size: 100px
                  - Color: BLUE_600 (brand color)
               c. Add title text "Learning Management System":
                  - Size: 32px (large, prominent)
                  - Weight: BOLD
                  - Alignment: CENTER
               d. Add subtitle text "Mobile Login":
                  - Size: 16px (medium)
                  - Color: GREY_700 (subtle)
                  - Alignment: CENTER
               e. Add 10px vertical spacing Container
               f. Add platform indicator text:
                  - Format: "Platform: {platform_name}"
                  - Size: 12px (small)
                  - Color: GREY_600 (very subtle)
                  - Alignment: CENTER
               g. Add 20px vertical spacing Container
            
            3. **Create Status Text**:
               a. Instantiate ft.Text with initial message
               b. Set text: "Sign in with your Google account"
               c. Set color: GREY_700 (neutral, informative)
               d. Set text_align: CENTER
               e. Store reference in self.status_text
               f. Append to self.controls
            
            4. **Create Login Button**:
               a. Instantiate ft.ElevatedButton with configuration:
                  - text: "Sign in with Google"
                  - icon: ft.Icons.LOGIN (sign-in icon)
                  - on_click: self.handle_login (event handler)
               b. Define button style:
                  - bgcolor: BLUE_600 (Google blue theme)
                  - color: WHITE (text color)
                  - padding: symmetric(horizontal=30, vertical=15)
               c. Set height to 50px (prominent, touch-friendly)
               d. Store reference in self.login_button
               e. Add 10px spacing Container before button
               f. Append button to self.controls
            
            5. **Create Progress Indicator**:
               a. Instantiate ft.ProgressRing (circular spinner)
               b. Set visible=False (hidden initially, shown during auth)
               c. Store reference in self.progress
               d. Append to self.controls

        Interactions:
            - **_get_platform_name()**: Retrieves platform name for display
            - **ft.Text, ft.Icon, ft.Container, ft.ElevatedButton, ft.ProgressRing**: 
              Flet UI components for interface construction

        Example:
            >>> # After initialization
            >>> login = FirebaseMobileLogin(page, auth, config, client_id)
            >>> # _build_ui already called in __init__
            >>> print(len(login.controls))
            12  # Header + status + button + progress + spacing
            >>> print(login.status_text.value)
            Sign in with your Google account
            >>> print(login.login_button.text)
            Sign in with Google
            >>> print(login.progress.visible)
            False

        See Also:
            - :meth:`_get_platform_name`: Platform detection helper
            - :meth:`handle_login`: Login button click handler
            - :meth:`__init__`: Calls this method during initialization

        Notes:
            - Components added to self.controls in display order (top to bottom)
            - Status text, login button, and progress stored for later updates
            - Button disabled during authentication (set in handle_login)
            - Progress initially hidden, shown when authentication starts
            - Spacing containers provide visual separation between sections
            - All text elements centered for mobile-friendly layout
            - Button height (50px) and padding optimized for touch input
        """
        platform_name = self._get_platform_name()
        
        self.controls.extend([
            ft.Container(height=50),
            ft.Icon(ft.Icons.CLOUD_CIRCLE, size=100, color=ft.Colors.BLUE_600),
            ft.Text("Learning Management System", size=32, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text("Mobile Login", size=16, color=ft.Colors.GREY_700, text_align=ft.TextAlign.CENTER),
            ft.Container(height=10),
            ft.Text(f"Platform: {platform_name}", size=12, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER),
            ft.Container(height=20)
        ])
        
        self.status_text = ft.Text("Sign in with your Google account", color=ft.Colors.GREY_700, text_align=ft.TextAlign.CENTER)
        self.controls.append(self.status_text)
        
        self.login_button = ft.ElevatedButton(
            text="Sign in with Google",
            icon=ft.Icons.LOGIN,
            on_click=self.handle_login,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE,
                padding=ft.padding.symmetric(horizontal=30, vertical=15),
            ),
            height=50
        )
        
        self.controls.extend([
            ft.Container(height=10),
            self.login_button
        ])
        
        self.progress = ft.ProgressRing(visible=False)
        self.controls.append(self.progress)

    def _get_platform_name(self):
        """Retrieve human-readable name of the current platform.

        Maps Flet's platform enumeration values to user-friendly display
        names for showing in the login interface. Helps users confirm
        they're on the correct device/platform.

        Returns:
            str: Human-readable platform name. Returns mapped name for known
                platforms (e.g., 'Android', 'iOS', 'Windows') or string
                representation of platform enum for unknown platforms.

        Algorithm:
            1. **Define Platform Mapping**:
               a. Create dictionary mapping ft.PagePlatform enums to strings
               b. Mappings:
                  - WINDOWS -> "Windows"
                  - LINUX -> "Linux"
                  - MACOS -> "macOS"
                  - ANDROID -> "Android"
                  - IOS -> "iOS"
               c. Store in platform_map variable
            
            2. **Lookup Current Platform**:
               a. Access self.page.platform (Flet PagePlatform enum)
               b. Use dict.get() with platform_map
               c. If platform in map: return mapped string
               d. If platform unknown: return str(self.page.platform)
            
            3. **Return Result**:
               a. Return human-readable platform name string

        Interactions:
            - **ft.Page**: Reads platform property for device detection
            - **ft.PagePlatform**: Enum values for different platforms

        Example:
            >>> # On Android device
            >>> login._get_platform_name()
            'Android'
            >>> 
            >>> # On iOS device
            >>> login._get_platform_name()
            'iOS'
            >>> 
            >>> # On Windows desktop
            >>> login._get_platform_name()
            'Windows'
            >>> 
            >>> # On unknown/future platform
            >>> # Assuming new platform enum value
            >>> login._get_platform_name()
            'PagePlatform.NEW_PLATFORM'

        See Also:
            - :meth:`_build_ui`: Uses this for platform display text
            - :class:`ft.PagePlatform`: Flet platform enumeration

        Notes:
            - Called during UI construction to display platform info
            - Provides user confirmation of correct device/platform
            - Gracefully handles unknown platforms with string conversion
            - Platform detection automatic via Flet framework
            - No external API calls or complex detection logic needed
        """
        platform_map = {
            ft.PagePlatform.WINDOWS: "Windows",
            ft.PagePlatform.LINUX: "Linux",
            ft.PagePlatform.MACOS: "macOS",
            ft.PagePlatform.ANDROID: "Android",
            ft.PagePlatform.IOS: "iOS"
        }
        return platform_map.get(self.page.platform, str(self.page.platform))

    def update_status(self, message, color=ft.Colors.BLUE_600):
        """Update the status message displayed to the user.

        Modifies the status text content and color to reflect the current
        authentication state. Used throughout the login flow to provide
        real-time feedback to the user.

        Args:
            message (str): Status message to display to user. Examples:
                "Opening browser...", "Waiting for sign-in...",
                "Authentication complete!", "Error: ...". Should be
                concise and informative.
            color (ft.Colors, optional): Text color for the status message.
                Used to indicate status type (blue=info, orange=warning,
                green=success, red=error). Defaults to ft.Colors.BLUE_600.

        Returns:
            None: Updates UI state and triggers page refresh as side effect.

        Algorithm:
            1. **Update Status Text**:
               a. Access self.status_text.value property
               b. Assign message parameter to value
               c. Text content updated in component state
            
            2. **Update Text Color**:
               a. Access self.status_text.color property
               b. Assign color parameter to color
               c. Color updated in component state
            
            3. **Refresh UI**:
               a. Call self.page.update()
               b. Flet re-renders affected components
               c. User sees updated message and color

        Interactions:
            - **ft.Text**: Modifies value and color properties
            - **ft.Page**: Calls update() to render changes

        Example:
            >>> # Show initial state
            >>> login.update_status(
            ...     "Sign in with your Google account",
            ...     ft.Colors.GREY_700
            ... )
            >>> 
            >>> # Show progress
            >>> login.update_status(
            ...     "Opening browser...",
            ...     ft.Colors.ORANGE
            ... )
            >>> 
            >>> # Show waiting state
            >>> login.update_status(
            ...     "Waiting for sign-in...",
            ...     ft.Colors.BLUE_600
            ... )
            >>> 
            >>> # Show success
            >>> login.update_status(
            ...     "Authentication complete!",
            ...     ft.Colors.GREEN_600
            ... )
            >>> 
            >>> # Show error
            >>> login.update_status(
            ...     "Error: Invalid credentials",
            ...     ft.Colors.RED_600
            ... )

        See Also:
            - :meth:`handle_login`: Uses this to show progress
            - :meth:`_handle_tokens`: Uses this to show success/failure
            - :meth:`_handle_timeout`: Uses this to show timeout

        Notes:
            - Called multiple times throughout authentication flow
            - Color coding follows standard conventions (green=success, red=error)
            - Message should be user-friendly and concise
            - Page update is synchronous (blocks until render complete)
            - Status text centered in UI for visibility
        """
        self.status_text.value = message
        self.status_text.color = color
        self.page.update()

    def handle_login(self, e):
        """Initiate the OAuth 2.0 authentication flow.

        Handles the login button click by generating a secure session ID,
        constructing the OAuth URL, launching the external browser, and
        starting background token polling. Manages UI state throughout
        the process with status updates and button state changes.

        Args:
            e (ft.ControlEvent): Flet control event from login button click.
                Contains event source and metadata. Not used in logic but
                required by Flet event handler signature.

        Returns:
            None: Initiates authentication flow with multiple side effects:
                - Generates and stores session_id
                - Updates UI status messages
                - Disables login button
                - Shows progress indicator
                - Launches external browser
                - Starts background polling thread

        Raises:
            Exception: Any exception during OAuth URL construction or browser
                launch is caught and displayed to user via status message.
                Login button re-enabled to allow retry.

        Algorithm:
            1. **Generate Session ID**:
               a. Call secrets.token_urlsafe(16)
               b. Generates 16-byte random token, base64url-encoded
               c. Store in self.session_id (used as OAuth state parameter)
               d. Provides CSRF protection and callback server lookup key
            
            2. **Update Initial Status**:
               a. Call update_status("Opening browser...", ORANGE)
               b. Indicates action in progress
               c. Orange color suggests transitional state
            
            3. **Disable Login Button**:
               a. Set self.login_button.disabled = True
               b. Prevents double-click / multiple sessions
               c. Button grayed out visually
            
            4. **Show Progress Indicator**:
               a. Set self.progress.visible = True
               b. Displays circular spinner
               c. Provides visual feedback of active process
            
            5. **Refresh UI**:
               a. Call self.page.update()
               b. Apply button and progress changes immediately
            
            6. **Try OAuth Flow**:
               a. Enter try block for error handling
               b. Call _build_oauth_url() to construct auth URL
               c. URL includes client_id, scopes, redirect_uri, state=session_id
               d. Store result in oauth_url variable
            
            7. **Launch Browser**:
               a. Call self.page.launch_url(oauth_url)
               b. Opens system browser to Google OAuth page
               c. User sees Google sign-in interface
               d. Non-blocking operation (returns immediately)
            
            8. **Update Waiting Status**:
               a. Call update_status("Waiting for sign-in...", BLUE_600)
               b. Indicates waiting for user action in browser
               c. Blue color suggests informational state
               d. Call page.update() to apply change
            
            9. **Start Polling**:
               a. Call _start_polling()
               b. Launches background thread to check for tokens
               c. Polls callback server every 5 seconds
               d. Thread runs independently of UI
            
            10. **Handle Errors**:
                a. Catch any Exception during OAuth flow
                b. Import traceback module for detailed error info
                c. Call update_status with error message (first 50 chars)
                d. Set status color to RED_600 (error indication)
                e. Re-enable login button: disabled = False
                f. Hide progress indicator: visible = False
                g. Print full error and traceback to console for debugging
                h. User can retry login after error

        Interactions:
            - **secrets.token_urlsafe()**: Generates secure session ID
            - **update_status()**: Shows progress messages to user
            - **_build_oauth_url()**: Constructs OAuth authorization URL
            - **ft.Page.launch_url()**: Opens external browser
            - **_start_polling()**: Starts background token retrieval

        Example:
            >>> # User clicks login button
            >>> login.handle_login(click_event)
            >>> # Output sequence:
            >>> # 1. Status: "Opening browser..." (orange)
            >>> # 2. Button disabled, progress shown
            >>> # 3. Browser launches to accounts.google.com
            >>> # 4. Status: "Waiting for sign-in..." (blue)
            >>> # 5. Polling thread starts in background
            >>> 
            >>> # If error occurs (e.g., network failure)
            >>> # Status: "Error: Failed to connect..." (red)
            >>> # Button re-enabled, progress hidden
            >>> # User can click to retry

        See Also:
            - :meth:`_build_oauth_url`: Constructs OAuth URL
            - :meth:`_start_polling`: Starts token polling thread
            - :meth:`update_status`: Updates status messages
            - :meth:`_handle_tokens`: Called when tokens received

        Notes:
            - Session ID provides CSRF protection via state parameter
            - Login button disabled to prevent multiple concurrent sessions
            - Progress indicator provides visual feedback during wait
            - Browser launch is non-blocking (immediate return)
            - Polling thread is daemon (won't block app exit)
            - Error messages truncated to 50 chars for UI display
            - Full errors printed to console for debugging
            - User can retry login after error by clicking button again
        """
        self.session_id = secrets.token_urlsafe(16)    
        self.update_status("Opening browser...", ft.Colors.ORANGE)
        self.login_button.disabled = True
        self.progress.visible = True
        self.page.update()
        
        try:
            oauth_url = self._build_oauth_url()
            
            self.page.launch_url(oauth_url)
            
            self.update_status("Waiting for sign-in...", ft.Colors.BLUE_600)
            self.page.update()
            
            self._start_polling()
            
        except Exception as ex:
            import traceback
            self.update_status(f"Error: {str(ex)[:50]}...", ft.Colors.RED_600)
            self.login_button.disabled = False
            self.progress.visible = False
            print(f"Mobile login error: {ex}\n{traceback.format_exc()}")
    
    def _build_oauth_url(self):
        """Construct the Google OAuth 2.0 authorization URL with parameters.

        Builds a complete OAuth URL including client ID, scopes, redirect URI,
        and state parameter for initiating the authentication flow. Uses
        implicit grant flow which returns tokens directly in URL fragment.

        Returns:
            str: Fully-formed OAuth authorization URL ready for browser launch.
                Format: 'https://accounts.google.com/o/oauth2/v2/auth?param=value&...'
                Includes all required OAuth parameters URL-encoded.

        Algorithm:
            1. **Set Base URL**:
               a. Define auth_url as Google OAuth 2.0 endpoint
               b. Value: "https://accounts.google.com/o/oauth2/v2/auth"
               c. This is Google's standard authorization endpoint
            
            2. **Define OAuth Parameters**:
               a. Create params dictionary with key-value pairs:
                  - client_id: self.oauth_client_id
                    (identifies the application to Google)
                  - redirect_uri: callback server URL
                    (where Google sends user after auth)
                    Value: 'https://lms-callback-git-main-astrallibertads-projects.vercel.app/callback.html'
                  - response_type: 'token'
                    (implicit grant - returns access_token in URL fragment)
                  - scope: space-separated OAuth scopes
                    Value: 'openid email profile https://www.googleapis.com/auth/drive'
                    (requests OpenID, user info, and Drive access)
                  - state: self.session_id
                    (CSRF protection and callback server token lookup key)
            
            3. **Encode Parameters**:
               a. Call urllib.parse.urlencode(params)
               b. Converts dictionary to URL query string
               c. Example: 'client_id=123&redirect_uri=https%3A%2F%2F...'
               d. Special characters percent-encoded for URL safety
            
            4. **Construct Complete URL**:
               a. Format string: f"{auth_url}?{encoded_params}"
               b. Combines base URL with encoded parameters
               c. Result: full OAuth authorization URL
            
            5. **Return URL**:
               a. Return complete URL string for browser launch

        Interactions:
            - **urllib.parse.urlencode()**: Encodes parameters for URL
            - **self.oauth_client_id**: Application OAuth client ID
            - **self.session_id**: Unique session identifier for state param

        Example:
            >>> login.session_id = 'abc123xyz'
            >>> login.oauth_client_id = '456-def.apps.googleusercontent.com'
            >>> url = login._build_oauth_url()
            >>> print(url)
            https://accounts.google.com/o/oauth2/v2/auth?client_id=456-def.apps.googleusercontent.com&redirect_uri=https%3A%2F%2Flms-callback...&response_type=token&scope=openid+email+profile+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdrive&state=abc123xyz
            >>> 
            >>> # URL components:
            >>> # - Base: accounts.google.com/o/oauth2/v2/auth
            >>> # - client_id: identifies app
            >>> # - redirect_uri: callback URL (encoded)
            >>> # - response_type: token (implicit grant)
            >>> # - scope: permissions requested (spaces -> +)
            >>> # - state: session ID for CSRF protection

        See Also:
            - :meth:`handle_login`: Calls this to get OAuth URL
            - :mod:`urllib.parse`: URL encoding utilities

        Notes:
            - Uses implicit grant flow (response_type=token)
            - Tokens returned in URL fragment (#access_token=...), not query
            - Callback URL must be authorized in Google Cloud Console
            - Scopes request OpenID, profile, email, and Drive access
            - State parameter (session_id) prevents CSRF attacks
            - Redirect URI points to callback server that stores tokens
            - URL encoding handles special characters in parameters
            - Scope parameter uses space-separated values (encoded as +)
        """
        auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            'client_id': self.oauth_client_id,
            'redirect_uri': 'https://lms-callback-git-main-astrallibertads-projects.vercel.app/callback.html',
            'response_type': 'token',
            'scope': 'openid email profile https://www.googleapis.com/auth/drive',
            'state': self.session_id
        }
        return f"{auth_url}?{urllib.parse.urlencode(params)}"
    
    def _start_polling(self):
        """Initiate background polling for OAuth token retrieval.

        Starts a daemon thread that periodically checks the callback server
        for OAuth tokens matching the current session ID. Polls every 5
        seconds for a maximum of 5 minutes (60 attempts). Handles token
        receipt and timeout scenarios.

        Returns:
            None: Starts background thread as side effect. Thread polls
                callback server and invokes handlers based on results.

        Algorithm:
            1. **Set Polling Flag**:
               a. Set self.polling = True
               b. Indicates polling thread is active
               c. Used to control loop continuation
            
            2. **Define Polling Function** (inner poll()):
               a. Set max_attempts = 60 (5 minutes total)
               b. Initialize attempt = 0 (counter)
               c. Enter while loop: while polling AND attempt < max_attempts
               
               d. **Update Status** (in loop):
                  - Call page.run_task(_update_waiting_status, attempt)
                  - Updates UI with animated dots on main thread
                  - Dots cycle: ".", "..", "..." based on attempt number
               
               e. **Try Token Check**:
                  i. Construct check_url for callback server
                     Format: 'https://lms-callback.vercel.app/api/token/{session_id}'
                  ii. Create urllib.request.Request with check_url
                  iii. Add 'Accept: application/json' header
                  iv. Try to open URL with 10-second timeout
                  v. Read and decode response as UTF-8
                  vi. Parse JSON response with json.loads()
                  vii. Check if response has 'success' and 'token' fields
                  viii. If token.access_token exists:
                       - Call page.run_task(_handle_tokens, token_info)
                       - Runs token handler on main thread
                       - Return from poll() function (exit loop)
                  ix. If HTTPError (404 = token not ready yet):
                      - Pass (ignore, continue polling)
                  x. If other exception during token check:
                      - Pass (ignore, continue polling)
               
               f. **Wait Between Attempts**:
                  i. Import time module
                  ii. Call time.sleep(5) to wait 5 seconds
                  iii. Increment attempt counter: attempt += 1
               
               g. **Handle General Errors**:
                  i. Catch any exception in outer try block
                  ii. Sleep 5 seconds
                  iii. Increment attempt counter
                  iv. Continue polling (resilient to transient errors)
               
               h. **Check Timeout** (after loop):
                  i. If attempt >= max_attempts:
                     - Call page.run_task(_handle_timeout)
                     - Notifies user of timeout on main thread
            
            3. **Create Polling Thread**:
               a. Instantiate threading.Thread
               b. Set target to poll function (defined above)
               c. Set daemon=True (thread exits when app exits)
               d. Thread won't block application shutdown
            
            4. **Start Thread**:
               a. Call thread.start()
               b. Thread begins executing poll() in background
               c. Main thread (UI) continues immediately
               d. Polling runs asynchronously

        Interactions:
            - **threading.Thread**: Creates background polling thread
            - **urllib.request**: Makes HTTP GET requests to callback server
            - **json.loads()**: Parses JSON token responses
            - **time.sleep()**: Waits between polling attempts
            - **page.run_task()**: Schedules UI updates on main thread
            - **_update_waiting_status()**: Updates status text with dots
            - **_handle_tokens()**: Processes received OAuth tokens
            - **_handle_timeout()**: Handles polling timeout

        Example:
            >>> # After handle_login() launches browser
            >>> login._start_polling()
            >>> # Polling thread starts in background
            >>> 
            >>> # Polling sequence (every 5 seconds):
            >>> # Attempt 1: Check callback server -> no token yet
            >>> # Status: "Waiting for sign-in."
            >>> # Attempt 2: Check callback server -> no token yet
            >>> # Status: "Waiting for sign-in.."
            >>> # Attempt 3: Check callback server -> no token yet
            >>> # Status: "Waiting for sign-in..."
            >>> # Attempt 4: Check callback server -> token found!
            >>> # Calls _handle_tokens(token_info)
            >>> # Polling stops
            >>> 
            >>> # If user never completes sign-in:
            >>> # After 60 attempts (5 minutes):
            >>> # Calls _handle_timeout()
            >>> # Status: "Timeout - Sign-in took too long"

        See Also:
            - :meth:`handle_login`: Calls this to start polling
            - :meth:`_update_waiting_status`: Updates status with dots
            - :meth:`_handle_tokens`: Processes tokens when received
            - :meth:`_handle_timeout`: Handles timeout after 5 minutes
            - :mod:`threading`: Thread-based parallelism

        Notes:
            - Polling runs for maximum 5 minutes (60 x 5 seconds)
            - Daemon thread exits automatically when app closes
            - HTTP 404 errors are expected (token not ready yet)
            - All UI updates run on main thread via page.run_task()
            - Transient network errors don't stop polling (resilient)
            - Polling stops immediately when token received
            - Callback server indexed by session_id for token lookup
            - 10-second timeout per HTTP request prevents long hangs
            - Status dots provide visual feedback that polling is active
        """
        self.polling = True
        
        def poll():
            max_attempts = 60
            attempt = 0
            
            while self.polling and attempt < max_attempts:
                self.page.run_task(self._update_waiting_status, attempt)
                
                try:
                    check_url = f"https://lms-callback.vercel.app/api/token/{self.session_id}"
                    
                    req = urllib.request.Request(check_url)
                    req.add_header('Accept', 'application/json')
                    
                    try:
                        with urllib.request.urlopen(req, timeout=10) as response:
                            response_text = response.read().decode('utf-8')
                            data = json.loads(response_text)
                            
                            if data.get('success') and data.get('token'):
                                token_info = data['token']
                                if token_info.get('access_token'):
                                    self.page.run_task(self._handle_tokens, token_info)
                                    return
                            
                    except urllib.error.HTTPError:
                        pass
                    except Exception:
                        pass
                    
                    import time
                    time.sleep(5)
                    attempt += 1
                    
                except Exception:
                    import time
                    time.sleep(5)
                    attempt += 1
            
            if attempt >= max_attempts:
                self.page.run_task(self._handle_timeout)
        
        thread = threading.Thread(target=poll, daemon=True)
        thread.start()
    
    async def _update_waiting_status(self, attempt):
        """Update status text with animated loading dots.

        Asynchronous method that modifies the status message to show cycling
        dots (., .., ...) indicating active polling. Provides visual feedback
        that the authentication process is ongoing.

        Args:
            attempt (int): Current polling attempt number (0-59). Used to
                calculate dot count via modulo operation. Cycles through
                1, 2, 3 dots repeatedly.

        Returns:
            None: Updates status_text value and triggers page refresh.

        Algorithm:
            1. **Calculate Dot Count**:
               a. Compute: (attempt % 3) + 1
               b. Result cycles through 1, 2, 3 as attempt increases
               c. Examples:
                  - attempt=0: (0%3)+1 = 1 dot
                  - attempt=1: (1%3)+1 = 2 dots
                  - attempt=2: (2%3)+1 = 3 dots
                  - attempt=3: (3%3)+1 = 1 dot (cycle repeats)
            
            2. **Build Dot String**:
               a. Use string multiplication: "." * dot_count
               b. Creates ".", "..", or "..." string
               c. Store in dots variable
            
            3. **Update Status Text**:
               a. Format message: f"Waiting for sign-in{dots}"
               b. Examples:
                  - "Waiting for sign-in."
                  - "Waiting for sign-in.."
                  - "Waiting for sign-in..."
               c. Assign to self.status_text.value
            
            4. **Refresh UI**:
               a. Call self.page.update()
               b. Flet renders updated status text
               c. User sees animated dots effect

        Interactions:
            - **ft.Text**: Modifies value property of status_text
            - **ft.Page**: Calls update() to render changes

        Example:
            >>> # Called from polling thread via page.run_task()
            >>> await login._update_waiting_status(0)
            >>> # Status: "Waiting for sign-in."
            >>> 
            >>> await login._update_waiting_status(1)
            >>> # Status: "Waiting for sign-in.."
            >>> 
            >>> await login._update_waiting_status(2)
            >>> # Status: "Waiting for sign-in..."
            >>> 
            >>> await login._update_waiting_status(3)
            >>> # Status: "Waiting for sign-in." (cycle repeats)
            >>> 
            >>> # Creates animation effect when called repeatedly:
            >>> for i in range(9):
            ...     await login._update_waiting_status(i)
            ...     # Shows: . .. ... . .. ... . .. ...

        See Also:
            - :meth:`_start_polling`: Calls this during polling loop
            - :meth:`update_status`: Alternative status update method

        Notes:
            - Must be called via page.run_task() from background thread
            - Async method for compatibility with Flet's async UI updates
            - Dot animation provides visual feedback of active process
            - Cycles every 3 attempts (1.5 seconds per cycle at 5s intervals)
            - Simple but effective loading indicator
            - No external dependencies (pure string manipulation)
        """
        dots = "." * ((attempt % 3) + 1)
        self.status_text.value = f"Waiting for sign-in{dots}"
        self.page.update()
    
    async def _handle_tokens(self, tokens):
        """Process received OAuth tokens and complete authentication.

        Asynchronous method that stops polling, constructs token data,
        authenticates with the auth service, and invokes the success
        callback. Handles both successful and failed authentication scenarios.

        Args:
            tokens (dict): OAuth token data from callback server containing:
                - access_token (str, required): OAuth access token for API calls
                - token_type (str, optional): Token type, typically 'Bearer'
                - expires_in (int, optional): Token lifetime in seconds
                - scope (str, optional): Space-separated granted OAuth scopes
                Example: {'access_token': 'ya29.a0...', 'token_type': 'Bearer',
                         'expires_in': 3599, 'scope': 'openid email profile...'}

        Returns:
            None: Completes authentication flow with multiple side effects:
                - Stops polling thread
                - Updates status messages
                - Authenticates with auth service
                - Invokes success callback
                - Updates button and progress states

        Algorithm:
            1. **Stop Polling**:
               a. Set self.polling = False
               b. Signals polling loop to exit
               c. Prevents further callback server checks
            
            2. **Update Status to Authenticating**:
               a. Call update_status("Authenticating...", GREEN_600)
               b. Indicates token received, processing in progress
               c. Green color suggests success imminent
               d. Call page.update() to render change
            
            3. **Construct Token Data**:
               a. Create token_data dictionary with fields:
                  - access_token: tokens.get('access_token')
                    (required, OAuth access token)
                  - token_type: tokens.get('token_type', 'Bearer')
                    (defaults to 'Bearer' if not provided)
                  - expires_in: tokens.get('expires_in')
                    (token lifetime in seconds, may be None)
                  - scope: tokens.get('scope')
                    (granted scopes, may be None)
                  - client_id: self.oauth_client_id
                    (application client ID for validation)
                  - client_secret: self.auth.client_secret
                    (from auth service for token refresh)
               b. All fields packaged for auth service processing
            
            4. **Authenticate with Auth Service**:
               a. Call self.auth.login_with_token(token_data)
               b. Auth service validates and stores credentials
               c. May verify token with Google API
               d. Store result in auth_result variable (boolean)
            
            5. **Handle Successful Authentication**:
               a. If auth_result is truthy (True):
                  i. Call update_status("Authentication complete!", GREEN_600)
                     - Shows success message to user
                     - Green color confirms success
                  ii. Set self.progress.visible = False
                      - Hides progress spinner
                  iii. Call self.page.update()
                       - Renders status and progress changes
                  iv. Check if self.on_success callback exists
                  v. If callback exists:
                      - Call self.on_success()
                      - Typically navigates to dashboard or main app
                      - Callback defined during initialization
            
            6. **Handle Failed Authentication**:
               a. If auth_result is falsy (False or None):
                  i. Call update_status("Authentication failed", RED_600)
                     - Shows error message
                     - Red color indicates failure
                  ii. Set self.login_button.disabled = False
                      - Re-enables login button for retry
                  iii. Set self.progress.visible = False
                       - Hides progress spinner
                  iv. Call self.page.update()
                      - Renders all UI changes
                  v. User can click login button to retry

        Interactions:
            - **GoogleAuth.login_with_token()**: Processes OAuth credentials
            - **update_status()**: Shows authentication progress/results
            - **ft.Page.update()**: Renders UI changes
            - **on_success callback**: Invoked after successful authentication

        Example:
            >>> # Tokens received from callback server
            >>> token_data = {
            ...     'access_token': 'ya29.a0AfH6SMBx...',
            ...     'token_type': 'Bearer',
            ...     'expires_in': 3599,
            ...     'scope': 'openid email profile https://www.googleapis.com/auth/drive'
            ... }
            >>> 
            >>> # Success scenario
            >>> await login._handle_tokens(token_data)
            >>> # Status: "Authenticating..." (green)
            >>> # Auth service processes token
            >>> # Status: "Authentication complete!" (green)
            >>> # Progress hidden
            >>> # on_success() called -> navigates to dashboard
            >>> 
            >>> # Failure scenario (invalid token)
            >>> await login._handle_tokens({'access_token': 'invalid'})
            >>> # Status: "Authenticating..." (green)
            >>> # Auth service rejects token
            >>> # Status: "Authentication failed" (red)
            >>> # Login button re-enabled
            >>> # Progress hidden

        See Also:
            - :meth:`_start_polling`: Calls this when tokens received
            - :class:`~src.services.google_auth.GoogleAuth`: Processes tokens
            - :meth:`handle_login`: Starts authentication flow

        Notes:
            - Must be called via page.run_task() from polling thread
            - Async method for Flet async UI updates
            - Stops polling immediately (no more callback server checks)
            - Token validation performed by auth service, not this method
            - Success callback optional (checked before invocation)
            - Failed auth allows retry by re-enabling login button
            - Token data includes client_id and client_secret for refresh
            - All UI updates synchronized via page.update()
        """
        self.polling = False
        
        self.update_status("Authenticating...", ft.Colors.GREEN_600)
        self.page.update()
        
        token_data = {
            'access_token': tokens.get('access_token'),
            'token_type': tokens.get('token_type', 'Bearer'),
            'expires_in': tokens.get('expires_in'),
            'scope': tokens.get('scope'),
            'client_id': self.oauth_client_id,
            'client_secret': self.auth.client_secret
        }
        
        auth_result = self.auth.login_with_token(token_data)
        
        if auth_result:
            from utils.common import show_snackbar
            self.update_status("Authentication complete!", ft.Colors.GREEN_600)
            self.progress.visible = False
            self.page.update()
            
            user_info = self.auth.get_user_info()
            if user_info:
                email = user_info.get("emailAddress")
                if email:
                    from services.fcm_integration import register_fcm_for_user
                    register_fcm_for_user(self.page, email)
                    show_snackbar(self.page, "FCM registration triggered for: " + email, ft.Colors.GREEN, duration=10)
                    print(f"✓ FCM registration triggered for: {email}")
            
            if self.on_success:
                self.on_success()
        else:
            self.update_status("Authentication failed", ft.Colors.RED_600)
            self.login_button.disabled = False
            self.progress.visible = False
            self.page.update()
    
    async def _handle_timeout(self):
        """Handle polling timeout when authentication takes too long.

        Asynchronous method that resets UI state and displays a timeout
        message when the maximum polling duration (5 minutes) is exceeded
        without receiving OAuth tokens. Allows user to retry login.

        Returns:
            None: Updates UI state to indicate timeout and enable retry.

        Algorithm:
            1. **Stop Polling**:
               a. Set self.polling = False
               b. Ensures polling loop exits (if not already exited)
               c. Prevents further callback server checks
            
            2. **Update Status Message**:
               a. Call update_status with timeout message
               b. Message: "Timeout - Sign-in took too long"
               c. Color: ft.Colors.ORANGE (warning color)
               d. Indicates user action needed (retry)
            
            3. **Re-enable Login Button**:
               a. Set self.login_button.disabled = False
               b. Allows user to click button again
               c. Enables retry of authentication flow
            
            4. **Hide Progress Indicator**:
               a. Set self.progress.visible = False
               b. Removes spinning progress ring
               c. Indicates process is no longer active
            
            5. **Refresh UI**:
               a. Call self.page.update()
               b. Applies all UI state changes
               c. User sees updated status, enabled button, no spinner

        Interactions:
            - **update_status()**: Shows timeout message to user
            - **ft.Page.update()**: Renders UI changes

        Example:
            >>> # After 60 polling attempts (5 minutes) without token
            >>> await login._handle_timeout()
            >>> # Status: "Timeout - Sign-in took too long" (orange)
            >>> # Login button: enabled (can retry)
            >>> # Progress indicator: hidden
            >>> 
            >>> # User can now click "Sign in with Google" again
            >>> # This starts a new session with fresh session_id

        See Also:
            - :meth:`_start_polling`: Calls this after max polling attempts
            - :meth:`handle_login`: User clicks button to retry

        Notes:
            - Timeout occurs after 60 attempts x 5 seconds = 5 minutes
            - Must be called via page.run_task() from polling thread
            - Async method for Flet async UI updates
            - Orange color suggests recoverable issue (not error)
            - Possible timeout causes:
              * User didn't complete sign-in in browser
              * User closed browser before completing
              * Network issues preventing callback server access
              * Callback server issues storing/retrieving tokens
            - User can retry immediately (no waiting period)
            - New retry generates new session_id for fresh attempt
            - No cleanup needed (polling already stopped)
        """
        self.polling = False
        self.update_status("Timeout - Sign-in took too long", ft.Colors.ORANGE)
        self.login_button.disabled = False
        self.progress.visible = False
        self.page.update()