"""Login UI Module.

This module provides login view components for the LMS application,
supporting both desktop and mobile OAuth authentication flows.

Classes:
    LoginBase: Abstract base class for login UI components.
    LoginView: Concrete login implementation with OAuth provider.

See Also:
    :class:`~src.ui.firebase_mobile_login.FirebaseMobileLogin`: Mobile-specific login.
    :class:`~src.services.auth_service.GoogleAuth`: Authentication service.
"""

import flet as ft
import traceback

from utils.common import show_snackbar


class LoginBase(ft.Column):
    """Abstract base class for login UI components with common authentication elements.

    LoginBase provides a reusable foundation for building login interfaces across
    different platforms and authentication flows. It encapsulates common UI elements
    (logo, title, status messages, login button) and defines a standard interface
    for handling authentication events. Subclasses implement platform-specific
    OAuth flows while inheriting the consistent UI structure and error handling.
    
    This class follows the Template Method pattern where the base class provides
    the UI framework and delegates authentication logic to subclasses through the
    abstract handle_login method. It manages UI state transitions during the
    authentication process and provides callbacks for success and error scenarios.

    Purpose:
        - Provide reusable base class for login UI components
        - Define standard login interface structure and layout
        - Manage authentication status messages and visual feedback
        - Handle success and error scenarios with consistent user experience
        - Abstract platform-specific authentication logic to subclasses
        - Support callback-based navigation after successful login

    Attributes:
        page (ft.Page): Flet page instance for UI rendering, platform detection,
            and page updates. Provides access to page.platform for device type
            detection and page.update() for UI refresh.
        auth (GoogleAuth): Authentication service managing OAuth credentials,
            token storage, and Drive API service initialization. Provides
            is_authenticated() check and platform-specific login methods.
        on_success (Callable or None): Optional callback function with no
            parameters, invoked after successful authentication. Typically
            handles navigation to main application view. Signature: () -> None.
        status_text (ft.Text): UI text element displaying current authentication
            status and messages to user. Color changes dynamically to indicate
            state (blue=info, green=success, red=error, grey=neutral).
        login_button (ft.ElevatedButton): Primary action button for initiating
            authentication flow. Disabled during authentication process, re-enabled
            on completion or error. Styled with Google brand colors.

    Interactions:
        - **ft.Column**: Parent class providing vertical layout container
        - **GoogleAuth**: Authentication service for credential management
        - **ft.Page**: Page instance for UI updates and platform detection
        - **ft.Text**: Status message display with dynamic color
        - **ft.ElevatedButton**: Login action button with event handling
        - **ft.Icon, ft.Container**: UI components for layout and branding

    Algorithm (High-Level Workflow):
        **Phase 1: Initialization**
            1. Call parent ft.Column constructor with centered layout settings
            2. Store references to page, auth service, and success callback
            3. Call _build_ui() to construct UI component tree
        
        **Phase 2: UI Construction** (_build_ui)
            1. Detect platform name for display
            2. Add header components (icon, title, subtitle, platform info)
            3. Create status text element for messages
            4. Create login button with click handler
            5. Add security notice text
            6. Append all components to self.controls
        
        **Phase 3: User Interaction** (handle_login - abstract)
            1. User clicks login button
            2. Subclass implementation handles platform-specific OAuth
            3. Authentication process executes
            4. Success or error handler invoked based on result
        
        **Phase 4: Success Handling** (handle_success)
            1. Update status to "Login successful!" (green)
            2. Check if on_success callback exists
            3. If callback exists, invoke it (typically navigates to dashboard)
        
        **Phase 5: Error Handling** (handle_error)
            1. Extract error message from exception
            2. Update status with error description (red)
            3. Re-enable login button for retry
            4. Log full error details to console for debugging

    Example:
        >>> # Define success handler
        >>> def on_login_success():
        ...     page.go('/dashboard')
        ...     print('User logged in successfully')
        >>> 
        >>> # Create concrete subclass (LoginView)
        >>> login = LoginView(
        ...     page=page,
        ...     provider=oauth_provider,
        ...     auth_service=auth,
        ...     on_success=on_login_success
        ... )
        >>> 
        >>> # Add to page
        >>> page.add(login)
        >>> page.update()
        >>> 
        >>> # User sees login UI with:
        >>> # - LMS logo and title
        >>> # - Status: "Please log in to continue"
        >>> # - "Login with Google" button
        >>> # - Platform indicator
        >>> # - Security notice
        >>> 
        >>> # User clicks login button -> subclass handles authentication
        >>> # On success -> status turns green -> on_login_success() called

    See Also:
        - :class:`LoginView`: Concrete implementation with OAuth provider
        - :class:`~src.ui.firebase_mobile_login.FirebaseMobileLogin`: Mobile login alternative
        - :class:`~src.services.google_auth.GoogleAuth`: Authentication service
        - :class:`ft.Column`: Parent Flet container class

    Notes:
        - Abstract class - cannot be instantiated directly
        - Subclasses must implement handle_login method
        - UI components stored as instance attributes for dynamic updates
        - Status color conventions: grey=neutral, blue=info, green=success, red=error
        - Login button automatically disabled during authentication
        - Success callback is optional (None check before invocation)
        - Platform detection automatic via Flet framework
        - All UI updates synchronized via page.update()

    Design Pattern:
        Template Method pattern - base class defines structure, subclasses
        implement specific authentication logic in handle_login().

    References:
        - Template Method Pattern: https://refactoring.guru/design-patterns/template-method
        - Flet UI Framework: https://flet.dev/docs/
        - Google OAuth 2.0: https://developers.google.com/identity/protocols/oauth2
    """

    def __init__(self, page, auth_service, on_success=None):
        """Initialize the LoginBase component with page and authentication services.

        Constructs the base login interface by setting up references to required
        services, configuring the parent Column layout, and building the UI
        component tree. Prepares the component for rendering and user interaction.

        Args:
            page (ft.Page): Flet page instance for UI updates, platform detection,
                and navigation. Must be initialized and active. Provides access
                to page.platform (device type) and page.update() (render trigger).
            auth_service (GoogleAuth): Authentication service for OAuth credential
                management. Must provide is_authenticated() method and platform-
                specific login methods (login_desktop(), login_mobile(), etc.).
            on_success (Callable, optional): Callback function invoked after
                successful authentication. Should handle navigation to main app.
                Signature: () -> None. Defaults to None (no action).

        Algorithm:
            1. **Initialize Parent Column**:
               a. Call super().__init__() with layout configuration
               b. Set controls to empty list (populated by _build_ui)
               c. Set alignment to MainAxisAlignment.CENTER (vertical centering)
               d. Set horizontal_alignment to CrossAxisAlignment.CENTER
               e. Set expand=True to fill available vertical space
               f. Set spacing=20 for consistent gaps between components
            
            2. **Store Service References**:
               a. Assign page parameter to self.page
               b. Assign auth_service to self.auth
               c. Assign on_success callback to self.on_success
            
            3. **Build User Interface**:
               a. Call self._build_ui()
               b. Constructs all UI components (logo, title, button, etc.)
               c. Populates self.controls with component tree
               d. Stores references to status_text and login_button
               e. Component now ready for rendering

        Interactions:
            - **ft.Column**: Parent class constructor for layout configuration
            - **_build_ui()**: Called to construct UI component tree

        Example:
            >>> # Create with minimal configuration
            >>> auth_service = GoogleAuth()
            >>> login_base = ConcreteLoginSubclass(
            ...     page=page,
            ...     auth_service=auth_service,
            ...     on_success=None
            ... )
            >>> 
            >>> # Create with success callback
            >>> def navigate_to_dashboard():
            ...     page.go('/dashboard')
            >>> 
            >>> login_with_callback = ConcreteLoginSubclass(
            ...     page=page,
            ...     auth_service=auth_service,
            ...     on_success=navigate_to_dashboard
            ... )
            >>> 
            >>> # Add to page for rendering
            >>> page.add(login_with_callback)
            >>> page.update()

        See Also:
            - :meth:`_build_ui`: Constructs the UI component tree
            - :class:`~src.services.google_auth.GoogleAuth`: Auth service requirements
            - :class:`ft.Column`: Parent Flet column container

        Notes:
            - Component is a Flet Column, can be added directly to page
            - UI components created in _build_ui, not in __init__
            - on_success callback is optional (None check before invocation)
            - All parameters except on_success are required
            - Component ready for rendering immediately after initialization
            - Subclasses should call super().__init__() first
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
        self.on_success = on_success
        self._build_ui()

    def _build_ui(self):
        """Construct and arrange all login interface UI components.

        Builds the complete user interface by creating and configuring all UI
        elements including header, status text, login button, and security notice.
        Arranges components in a centered, vertically-stacked layout with
        consistent spacing and styling.

        Returns:
            None: Modifies self.controls list in place with UI components.
                Also stores references to status_text and login_button in
                instance attributes for dynamic updates.

        Algorithm:
            1. **Detect Platform**:
               a. Call _get_platform_name() to get human-readable platform name
               b. Store result in platform_name variable
               c. Used for display text (e.g., "Platform: Windows")
            
            2. **Add Header Components**:
               a. Add 50px vertical spacing Container at top
               b. Add cloud icon (ft.Icons.CLOUD_CIRCLE):
                  - Size: 100px
                  - Color: BLUE_600 (brand blue)
               c. Add title text "Learning Management System":
                  - Size: 32px (large, prominent)
                  - Weight: BOLD
                  - Alignment: CENTER
               d. Add subtitle text "Access your learning materials anywhere":
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
               b. Set text: "Please log in to continue"
               c. Set color: GREY_700 (neutral, informative)
               d. Set text_align: CENTER
               e. Store reference in self.status_text
               f. Append to self.controls
            
            4. **Create Login Button**:
               a. Instantiate ft.ElevatedButton with configuration:
                  - text: "Login with Google"
                  - icon: ft.Icons.LOGIN (sign-in icon)
                  - on_click: self.handle_login (delegated to subclass)
               b. Define button style:
                  - bgcolor: BLUE_600 (Google blue theme)
                  - color: WHITE (text color)
                  - padding: symmetric(horizontal=30, vertical=15)
               c. Set height to 50px (prominent, touch-friendly)
               d. Store reference in self.login_button
               e. Add 10px spacing Container before button
               f. Append button to self.controls
            
            5. **Add Security Notice**:
               a. Add 20px vertical spacing Container
               b. Add security text:
                  - Content: "Secure authentication via Google OAuth 2.0"
                  - Size: 12px (small, informational)
                  - Color: GREY_500 (very subtle)
                  - Alignment: CENTER
                  - Italic: True (distinguishes from other text)
               c. Append to self.controls

        Interactions:
            - **_get_platform_name()**: Retrieves platform name for display
            - **ft.Text, ft.Icon, ft.Container, ft.ElevatedButton**: 
              Flet UI components for interface construction
            - **handle_login()**: Abstract method called on button click

        Example:
            >>> # After initialization
            >>> login = ConcreteLoginSubclass(page, auth, callback)
            >>> # _build_ui already called in __init__
            >>> print(len(login.controls))
            14  # Header + status + button + security notice + spacing
            >>> print(login.status_text.value)
            Please log in to continue
            >>> print(login.login_button.text)
            Login with Google
            >>> print(login.login_button.disabled)
            False

        See Also:
            - :meth:`_get_platform_name`: Platform detection helper
            - :meth:`handle_login`: Login button click handler (abstract)
            - :meth:`__init__`: Calls this method during initialization

        Notes:
            - Components added to self.controls in display order (top to bottom)
            - Status text and login button stored for later updates
            - Button enabled initially, disabled during authentication
            - Spacing containers provide visual separation between sections
            - All text elements centered for mobile-friendly layout
            - Button height (50px) and padding optimized for touch input
            - Security notice builds user trust and transparency
        """
        platform_name = self._get_platform_name()
        
        self.controls.extend([
            ft.Container(height=50),
            ft.Icon(ft.Icons.CLOUD_CIRCLE, size=100, color=ft.Colors.BLUE_600),
            ft.Text("Learning Management System", size=32, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text("Access your learning materials anywhere", size=16, color=ft.Colors.GREY_700, text_align=ft.TextAlign.CENTER),
            ft.Container(height=10),
            ft.Text(f"Platform: {platform_name}", size=12, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER),
            ft.Container(height=20)
        ])
        
        self.status_text = ft.Text("Please log in to continue", color=ft.Colors.GREY_700, text_align=ft.TextAlign.CENTER)
        self.controls.append(self.status_text)
        
        self.login_button = ft.ElevatedButton(
            text="Login with Google",
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
            self.login_button,
            ft.Container(height=20),
            ft.Text("Secure authentication via Google OAuth 2.0", size=12, color=ft.Colors.GREY_500, 
                   text_align=ft.TextAlign.CENTER, italic=True)
        ])

    def _get_platform_name(self):
        """Retrieve human-readable name of the current platform.

        Maps Flet's platform enumeration values to user-friendly display
        names for showing in the login interface. Helps users confirm
        they're on the correct device/platform.

        Returns:
            str: Human-readable platform name. Returns mapped name for known
                platforms (e.g., 'Windows', 'Android', 'macOS') or string
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
            >>> # On Windows desktop
            >>> login._get_platform_name()
            'Windows'
            >>> 
            >>> # On Android device
            >>> login._get_platform_name()
            'Android'
            >>> 
            >>> # On macOS
            >>> login._get_platform_name()
            'macOS'
            >>> 
            >>> # On unknown/future platform
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

    def update_status(self, message, color=ft.Colors.BLUE_600, disable_button=None):
        """Update the status message and optionally control button state.

        Modifies the status text content and color to reflect the current
        authentication state. Optionally disables or enables the login button
        to prevent user actions during processing. Used throughout the login
        flow to provide real-time feedback.

        Args:
            message (str): Status message to display to user. Examples:
                "Please log in to continue", "Opening browser...",
                "Login successful!", "Login failed: ...". Should be
                concise and user-friendly.
            color (ft.Colors, optional): Text color for the status message.
                Used to indicate status type (blue=info, orange=warning,
                green=success, red=error). Defaults to ft.Colors.BLUE_600.
            disable_button (bool or None, optional): If provided, sets the
                login button's disabled state. True disables button (during
                auth), False enables button (after completion/error), None
                leaves current state unchanged. Defaults to None.

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
            
            3. **Update Button State** (if disable_button provided):
               a. Check if disable_button parameter is not None
               b. If not None:
                  i. Access self.login_button.disabled property
                  ii. Assign disable_button value to disabled
                  iii. Button state updated (True=disabled, False=enabled)
               c. If None: button state unchanged
            
            4. **Refresh UI**:
               a. Call self.page.update()
               b. Flet re-renders affected components
               c. User sees updated message, color, and button state

        Interactions:
            - **ft.Text**: Modifies value and color properties
            - **ft.ElevatedButton**: Modifies disabled property
            - **ft.Page**: Calls update() to render changes

        Example:
            >>> # Show initial state
            >>> login.update_status(
            ...     "Please log in to continue",
            ...     ft.Colors.GREY_700,
            ...     disable_button=False
            ... )
            >>> 
            >>> # Show progress (disable button)
            >>> login.update_status(
            ...     "Opening browser for authentication...",
            ...     ft.Colors.BLUE_600,
            ...     disable_button=True
            ... )
            >>> 
            >>> # Show success (leave button disabled)
            >>> login.update_status(
            ...     "Login successful!",
            ...     ft.Colors.GREEN_600,
            ...     disable_button=None
            ... )
            >>> 
            >>> # Show error (re-enable button)
            >>> login.update_status(
            ...     "Login failed: Invalid credentials",
            ...     ft.Colors.RED_600,
            ...     disable_button=False
            ... )

        See Also:
            - :meth:`handle_success`: Uses this to show success
            - :meth:`handle_error`: Uses this to show errors
            - :meth:`handle_login`: Uses this to show progress

        Notes:
            - Called multiple times throughout authentication flow
            - Color coding follows standard conventions (green=success, red=error)
            - Message should be user-friendly and concise
            - disable_button parameter provides fine control over button state
            - Page update is synchronous (blocks until render complete)
            - Status text centered in UI for visibility
            - Button disable prevents double-click during authentication
        """
        self.status_text.value = message
        self.status_text.color = color
        if disable_button is not None:
            self.login_button.disabled = disable_button
        self.page.update()

    def handle_success(self):
        """Handle successful authentication completion.

        Updates the UI to display success message and invokes the success
        callback to navigate to the main application view. Called by subclass
        implementations after successful OAuth token retrieval and validation.

        Returns:
            None: Updates UI and invokes callback as side effects.

        Algorithm:
            1. **Update Status Display**:
               a. Call update_status() with success message
               b. Message: "Login successful!"
               c. Color: ft.Colors.GREEN_600 (success color)
               d. Button state: not changed (remains in current state)
            
            2. **Invoke Success Callback**:
               a. Check if self.on_success is not None
               b. If callback exists:
                  i. Call self.on_success()
                  ii. Callback typically navigates to dashboard
                  iii. May perform additional setup (load user data, etc.)
               c. If callback is None:
                  i. No action taken
                  ii. UI shows success message only

        Interactions:
            - **update_status()**: Shows success message to user
            - **on_success callback**: Invoked for post-login navigation

        Example:
            >>> # Define success callback
            >>> def on_login_success():
            ...     page.go('/dashboard')
            ...     load_user_data()
            ...     print('Login complete')
            >>> 
            >>> login = LoginView(page, provider, auth, on_login_success)
            >>> 
            >>> # After successful authentication
            >>> login.handle_success()
            >>> # Status: "Login successful!" (green)
            >>> # on_login_success() called
            >>> # User navigated to dashboard

        See Also:
            - :meth:`update_status`: Updates status message
            - :meth:`handle_error`: Handles authentication failures
            - :meth:`handle_login`: Initiates authentication flow

        Notes:
            - Called by subclass after successful OAuth token validation
            - Success callback is optional (None check performed)
            - Callback should handle navigation and post-login setup
            - UI update provides visual confirmation before navigation
            - Button state not explicitly changed (typically already disabled)
            - Callback may trigger page navigation (removes login view)
        """
        self.update_status("Login successful!", ft.Colors.GREEN_600)
        if self.on_success:
            self.on_success()

    def handle_error(self, error, context="Login"):
        """Display error message and log detailed error information.

        Handles authentication errors by updating the UI with a user-friendly
        error message, re-enabling the login button for retry, and logging
        detailed error information to the console for debugging. Truncates
        long error messages for UI display.

        Args:
            error (Exception): The exception that occurred during authentication.
                Can be any Exception subclass (ValueError, ConnectionError, etc.).
                Error message extracted via str(error).
            context (str, optional): Context description for error logging and
                display. Prepended to error message. Examples: "Login",
                "Desktop login", "Browser launch". Defaults to "Login".

        Returns:
            None: Updates UI, logs error, and re-enables button as side effects.

        Algorithm:
            1. **Extract Error Message**:
               a. Convert error to string: str(error)
               b. Store in error_msg variable
               c. Full message preserved for logging
            
            2. **Update UI with Error**:
               a. Truncate error_msg to first 50 characters
               b. Append "..." if truncated
               c. Format message: "{context} failed: {error_msg[:50]}..."
               d. Call update_status() with:
                  i. Formatted error message
                  ii. Color: ft.Colors.RED_600 (error indication)
                  iii. disable_button: False (re-enable for retry)
               e. User sees error message and enabled button
            
            3. **Log Detailed Error**:
               a. Format console message: "{context} error: {error}"
               b. Get full stack trace: traceback.format_exc()
               c. Print formatted message with full traceback
               d. Includes exception type, message, and call stack
               e. Available in console for debugging

        Interactions:
            - **update_status()**: Shows error message to user
            - **traceback.format_exc()**: Gets full exception traceback
            - **str()**: Converts exception to string message

        Example:
            >>> # Network error during authentication
            >>> try:
            ...     perform_oauth_request()
            ... except ConnectionError as e:
            ...     login.handle_error(e, "Desktop login")
            >>> # Status: "Desktop login failed: Failed to connect..." (red)
            >>> # Button: enabled (user can retry)
            >>> # Console: "Desktop login error: Failed to connect to server"
            >>> #          "Traceback (most recent call last):"
            >>> #          "  File '...', line ..., in perform_oauth_request"
            >>> #          "ConnectionError: Failed to connect to server"
            >>> 
            >>> # Generic error with long message
            >>> try:
            ...     auth.login()
            ... except ValueError as e:
            ...     login.handle_error(e, "Login")
            >>> # Status: "Login failed: The authentication token is inval..." (red)

        See Also:
            - :meth:`update_status`: Updates status message and button
            - :meth:`handle_success`: Handles successful authentication
            - :mod:`traceback`: Python traceback module for error logging

        Notes:
            - Error message truncated to 50 chars for UI display
            - Full error logged to console for debugging
            - Login button re-enabled to allow retry
            - Red color clearly indicates error state
            - Stack trace helps developers diagnose issues
            - Context parameter helps identify error source
            - Safe for any Exception subclass
        """
        error_msg = str(error)
        self.update_status(f"{context} failed: {error_msg[:50]}...", ft.Colors.RED_600, False)
        print(f"{context} error: {error}\n{traceback.format_exc()}")

    def handle_login(self, e):
        """Handle login button click event. Must be implemented by subclasses.

        Abstract method that delegates authentication logic to concrete
        subclass implementations. Different platforms require different
        OAuth flows (desktop local server vs mobile browser redirect).

        Args:
            e (ft.ControlEvent): Flet control event from login button click.
                Contains event source and metadata. Available to subclass
                implementations if needed.

        Returns:
            None: Subclass implementations handle authentication flow.

        Raises:
            NotImplementedError: Always raised if called on LoginBase directly.
                Message: "Subclasses must implement handle_login"

        Algorithm:
            1. **Raise NotImplementedError**:
               a. Create NotImplementedError with descriptive message
               b. Message: "Subclasses must implement handle_login"
               c. Raise exception to signal abstract method
               d. Prevents instantiation of LoginBase directly

        Interactions:
            - **Subclass implementations**: Must override this method

        Example:
            >>> # Attempting to use LoginBase directly fails
            >>> login_base = LoginBase(page, auth, callback)
            >>> login_base.handle_login(click_event)
            NotImplementedError: Subclasses must implement handle_login
            >>> 
            >>> # Concrete subclass implementation
            >>> class ConcreteLogin(LoginBase):
            ...     def handle_login(self, e):
            ...         self.update_status("Authenticating...", disable_button=True)
            ...         self.auth.login_desktop()
            ...         if self.auth.is_authenticated():
            ...             self.handle_success()
            ...         else:
            ...             self.handle_error(Exception("Auth failed"))
            >>> 
            >>> concrete = ConcreteLogin(page, auth, callback)
            >>> concrete.handle_login(click_event)
            >>> # Works correctly - subclass provides implementation

        See Also:
            - :class:`LoginView`: Concrete implementation with OAuth provider
            - :meth:`handle_success`: Called on successful authentication
            - :meth:`handle_error`: Called on authentication failure

        Notes:
            - Abstract method - must be overridden by subclasses
            - LoginBase cannot be instantiated directly (design choice)
            - Subclasses implement platform-specific OAuth flows
            - Event parameter available but typically unused
            - Template Method pattern - defines interface, delegates implementation
        """
        raise NotImplementedError("Subclasses must implement handle_login")


class LoginView(LoginBase):
    """Concrete login implementation with OAuth provider and platform detection.

    LoginView extends LoginBase to provide a complete login solution that
    automatically detects the platform (desktop vs mobile) and executes the
    appropriate OAuth 2.0 authentication flow. Desktop platforms use a local
    HTTP server for OAuth callback handling, while mobile platforms launch
    an external browser with redirect-based authentication.

    Purpose:
        - Provide platform-aware OAuth 2.0 authentication
        - Support desktop login with local callback server
        - Support mobile login with browser redirect
        - Integrate with GoogleOAuthProvider for OAuth configuration
        - Handle platform detection and flow selection automatically
        - Provide seamless authentication experience across all platforms

    Attributes:
        provider (GoogleOAuthProvider): Flet OAuth provider instance containing
            OAuth configuration (client_id, client_secret, redirect_url, scopes).
            Used for building OAuth URLs and handling callbacks.
        page (ft.Page): Inherited from LoginBase. Flet page instance.
        auth (GoogleAuth): Inherited from LoginBase. Authentication service.
        on_success (Callable): Inherited from LoginBase. Success callback.
        status_text (ft.Text): Inherited from LoginBase. Status display.
        login_button (ft.ElevatedButton): Inherited from LoginBase. Login button.

    Interactions:
        - **LoginBase**: Parent class providing UI framework and common methods
        - **GoogleOAuthProvider**: Provides OAuth configuration and credentials
        - **GoogleAuth**: Handles token storage and authentication validation
        - **ft.Page**: Platform detection and browser launching
        - **urllib.parse**: URL encoding for OAuth parameters

    Algorithm (High-Level Workflow):
        **Phase 1: Initialization**
            1. Store OAuth provider reference
            2. Call parent LoginBase.__init__() to build UI
            3. Component ready for rendering
        
        **Phase 2: Login Initiation** (handle_login)
            1. Detect platform type (desktop vs mobile)
            2. Check if platform in [WINDOWS, LINUX, MACOS]
            3. If desktop: call _handle_desktop_login()
            4. If mobile: call _handle_mobile_login()
        
        **Phase 3: Desktop Authentication** (_handle_desktop_login)
            1. Update status to "Opening browser for authentication..."
            2. Disable login button
            3. Call auth.login_desktop() - starts local server, opens browser
            4. Wait for user to complete OAuth in browser
            5. Check auth.is_authenticated()
            6. If authenticated: call handle_success()
            7. If not authenticated: show error message
            8. On exception: call handle_error()
        
        **Phase 4: Mobile Authentication** (_handle_mobile_login)
            1. Update status to "Opening browser..."
            2. Disable login button
            3. Build OAuth URL with authorization code flow parameters
            4. Include client_id, redirect_uri, scopes, access_type, prompt
            5. Launch external browser with OAuth URL
            6. Update status with instruction to return to app
            7. Show snackbar notification about browser opening
            8. User completes auth in browser (handled externally)
            9. On exception: call handle_error()

    Example:
        >>> # Setup OAuth provider
        >>> from flet.auth.providers import GoogleOAuthProvider
        >>> provider = GoogleOAuthProvider(
        ...     client_id='123456-abc.apps.googleusercontent.com',
        ...     client_secret='secret_key',
        ...     redirect_url='http://localhost:8080/callback'
        ... )
        >>> 
        >>> # Define success callback
        >>> def on_login_success():
        ...     page.go('/dashboard')
        ...     print('Login successful!')
        >>> 
        >>> # Create login view
        >>> login = LoginView(
        ...     page=page,
        ...     provider=provider,
        ...     auth_service=auth,
        ...     on_success=on_login_success
        ... )
        >>> 
        >>> # Add to page
        >>> page.add(login)
        >>> page.update()
        >>> 
        >>> # Desktop user clicks login:
        >>> # -> Browser opens to accounts.google.com
        >>> # -> User signs in with Google account
        >>> # -> Browser redirects to localhost:8080/callback
        >>> # -> Local server captures OAuth code
        >>> # -> Token exchanged and stored
        >>> # -> on_login_success() called -> dashboard
        >>> 
        >>> # Mobile user clicks login:
        >>> # -> Browser opens to accounts.google.com
        >>> # -> User signs in with Google account
        >>> # -> Browser redirects to configured callback URL
        >>> # -> External callback handler processes token
        >>> # -> User returns to app manually

    See Also:
        - :class:`LoginBase`: Parent class with UI framework
        - :class:`~src.ui.firebase_mobile_login.FirebaseMobileLogin`: Alternative mobile implementation
        - :class:`~src.services.google_auth.GoogleAuth`: Authentication service
        - :class:`~flet.auth.providers.GoogleOAuthProvider`: OAuth provider configuration

    Notes:
        - Platform detection based on ft.PagePlatform enum
        - Desktop platforms: Windows, Linux, macOS
        - Mobile platforms: Android, iOS
        - Desktop uses authorization code flow with local server
        - Mobile uses authorization code flow with external callback
        - Both flows require OAuth 2.0 client credentials
        - Provider must be configured with correct redirect URLs
        - Desktop redirect: typically http://localhost:{PORT}/callback
        - Mobile redirect: must match OAuth client configuration
        - Error handling consistent across both flows
        - Success callback shared between desktop and mobile flows
    """

    def __init__(self, page, provider, auth_service, on_success=None):
        """Initialize LoginView with OAuth provider and configuration.

        Constructs the login view by storing the OAuth provider reference
        and delegating UI construction to the parent LoginBase class.

        Args:
            page (ft.Page): Flet page instance for UI updates and platform
                detection. Must be initialized and active.
            provider (GoogleOAuthProvider): Flet OAuth provider containing
                OAuth 2.0 configuration (client_id, client_secret, redirect_url,
                scopes). Must be properly configured with Google Cloud Console
                credentials.
            auth_service (GoogleAuth): Authentication service for token
                management and credential storage. Must provide login_desktop()
                method and is_authenticated() check.
            on_success (Callable, optional): Callback function invoked after
                successful authentication. Signature: () -> None. Defaults to None.

        Algorithm:
            1. **Store OAuth Provider**:
               a. Assign provider parameter to self.provider
               b. Makes provider available to authentication methods
            
            2. **Initialize Parent Class**:
               a. Call super().__init__() with page, auth_service, on_success
               b. Parent constructs UI components
               c. Parent stores page, auth, and callback references
               d. Component ready for rendering

        Interactions:
            - **LoginBase.__init__()**: Parent class initialization
            - **GoogleOAuthProvider**: OAuth configuration storage

        Example:
            >>> # Create OAuth provider
            >>> provider = GoogleOAuthProvider(
            ...     client_id='client_id',
            ...     client_secret='secret',
            ...     redirect_url='http://localhost:8080/callback'
            ... )
            >>> 
            >>> # Create login view
            >>> login = LoginView(
            ...     page=page,
            ...     provider=provider,
            ...     auth_service=auth,
            ...     on_success=lambda: page.go('/dashboard')
            ... )
            >>> 
            >>> # Access provider in methods
            >>> print(login.provider.client_id)
            client_id

        See Also:
            - :meth:`LoginBase.__init__`: Parent class initialization
            - :class:`~flet.auth.providers.GoogleOAuthProvider`: Provider class

        Notes:
            - Provider stored before parent initialization
            - Provider accessible in all instance methods
            - Parent __init__ builds UI components
            - All LoginBase attributes inherited
        """
        self.provider = provider
        super().__init__(page, auth_service, on_success)

    def handle_login(self, e):
        """Handle login button click with platform-specific authentication flow.

        Detects the current platform and routes to the appropriate OAuth
        authentication method. Desktop platforms use local server callback,
        mobile platforms use external browser redirect.

        Args:
            e (ft.ControlEvent): Flet control event from login button click.
                Not used in logic but required by Flet event handler signature.

        Returns:
            None: Delegates to platform-specific authentication methods.

        Algorithm:
            1. **Platform Detection**:
               a. Define desktop platforms list:
                  i. ft.PagePlatform.WINDOWS
                  ii. ft.PagePlatform.LINUX
                  iii. ft.PagePlatform.MACOS
               b. Check if self.page.platform in desktop platforms list
               c. Store result in is_desktop boolean
            
            2. **Route to Appropriate Handler**:
               a. If is_desktop is True:
                  i. Call self._handle_desktop_login()
                  ii. Uses local HTTP server for OAuth callback
               b. If is_desktop is False (mobile):
                  i. Call self._handle_mobile_login()
                  ii. Uses external browser with redirect URL

        Interactions:
            - **ft.Page.platform**: Reads platform enum for detection
            - **_handle_desktop_login()**: Desktop OAuth flow
            - **_handle_mobile_login()**: Mobile OAuth flow

        Example:
            >>> # On Windows desktop
            >>> login.page.platform = ft.PagePlatform.WINDOWS
            >>> login.handle_login(click_event)
            >>> # Routes to _handle_desktop_login()
            >>> # Local server starts on localhost
            >>> # Browser opens to Google OAuth
            >>> 
            >>> # On Android mobile
            >>> login.page.platform = ft.PagePlatform.ANDROID
            >>> login.handle_login(click_event)
            >>> # Routes to _handle_mobile_login()
            >>> # External browser opens to Google OAuth
            >>> # Redirect handled externally

        See Also:
            - :meth:`_handle_desktop_login`: Desktop authentication flow
            - :meth:`_handle_mobile_login`: Mobile authentication flow
            - :class:`ft.PagePlatform`: Platform enumeration

        Notes:
            - Platform detection automatic via Flet
            - Desktop: Windows, Linux, macOS
            - Mobile: Android, iOS, other platforms
            - Clear separation between desktop and mobile flows
            - Event parameter required but unused
        """
        is_desktop = self.page.platform in [
            ft.PagePlatform.WINDOWS,
            ft.PagePlatform.LINUX,
            ft.PagePlatform.MACOS
        ]

        if is_desktop:
            self._handle_desktop_login()
        else:
            self._handle_mobile_login()

    def _handle_desktop_login(self):
        """Execute desktop OAuth flow with local callback server.

        Performs OAuth 2.0 authentication on desktop platforms using a
        temporary local HTTP server to handle the OAuth callback. Opens
        the system browser for user authentication and waits for the
        callback with authorization code.

        Returns:
            None: Updates UI and invokes callbacks based on authentication result.

        Algorithm:
            1. **Update UI for Processing**:
               a. Call update_status() with message
               b. Message: "Opening browser for authentication..."
               c. Color: default (blue)
               d. disable_button: True (prevents double-click)
            
            2. **Try Desktop Authentication**:
               a. Enter try block for error handling
               b. Call self.auth.login_desktop()
               c. Auth service performs:
                  i. Start local HTTP server on available port
                  ii. Build OAuth URL with redirect to localhost
                  iii. Open system browser to OAuth URL
                  iv. Wait for user to authenticate
                  v. Receive callback with authorization code
                  vi. Exchange code for access token
                  vii. Store credentials in auth service
               d. login_desktop() method blocks until complete or timeout
            
            3. **Check Authentication Result**:
               a. Call self.auth.is_authenticated()
               b. Returns True if credentials valid and stored
               c. If True (authenticated):
                  i. Call self.handle_success()
                  ii. Shows success message (green)
                  iii. Invokes on_success callback
                  iv. Typically navigates to dashboard
               d. If False (not authenticated):
                  i. Call update_status() with error message
                  ii. Message: "Login completed but authentication failed"
                  iii. Color: RED_600 (error indication)
                  iv. disable_button: False (re-enable for retry)
            
            4. **Handle Exceptions**:
               a. Catch any Exception during authentication
               b. Examples: NetworkError, TimeoutError, ValueError
               c. Call self.handle_error(ex, "Desktop login")
               d. handle_error displays user message and logs details

        Interactions:
            - **update_status()**: Shows progress and results
            - **GoogleAuth.login_desktop()**: Executes OAuth flow
            - **GoogleAuth.is_authenticated()**: Validates credentials
            - **handle_success()**: Handles successful authentication
            - **handle_error()**: Handles authentication failures

        Example:
            >>> # Successful desktop login
            >>> login._handle_desktop_login()
            >>> # Status: "Opening browser for authentication..." (blue)
            >>> # Button: disabled
            >>> # Browser opens: accounts.google.com OAuth page
            >>> # User signs in with Google account
            >>> # Browser redirects: http://localhost:8080/callback?code=...
            >>> # Local server captures code
            >>> # Token exchanged and stored
            >>> # Status: "Login successful!" (green)
            >>> # on_success() called -> navigate to dashboard
            >>> 
            >>> # Failed desktop login (user cancels)
            >>> login._handle_desktop_login()
            >>> # Status: "Opening browser for authentication..."
            >>> # Browser opens
            >>> # User cancels OAuth consent
            >>> # login_desktop() returns without storing credentials
            >>> # is_authenticated() returns False
            >>> # Status: "Login completed but authentication failed" (red)
            >>> # Button: enabled for retry

        See Also:
            - :meth:`handle_login`: Routes to this for desktop platforms
            - :class:`~src.services.google_auth.GoogleAuth`: Provides login_desktop()
            - :meth:`handle_success`: Called on successful authentication
            - :meth:`handle_error`: Called on exceptions

        Notes:
            - Blocks during authentication (synchronous flow)
            - Local server starts on random available port
            - Server automatically stops after callback received
            - Browser opens automatically via auth service
            - User must complete OAuth in browser
            - Timeout typically 5 minutes for user to authenticate
            - Network errors handled gracefully
            - Button re-enabled on failure for retry
            - Success callback handles navigation
        """
        self.update_status("Opening browser for authentication...", disable_button=True)
        
        try:
            self.auth.login_desktop()
            
            if self.auth.is_authenticated():
                self.handle_success()
            else:
                self.update_status("Login completed but authentication failed", ft.Colors.RED_600, False)
                     
        except Exception as ex:
            self.handle_error(ex, "Desktop login")

    def _handle_mobile_login(self):
        """Execute mobile OAuth flow with external browser redirect.

        Performs OAuth 2.0 authentication on mobile platforms by launching
        the system browser with OAuth URL. Uses authorization code flow with
        external redirect URL that must be handled by a callback server or
        deep link handler.

        Returns:
            None: Opens browser and updates UI. Token handling occurs externally.

        Algorithm:
            1. **Import URL Encoding Module**:
               a. Import urllib.parse for URL parameter encoding
               b. Used to safely encode OAuth parameters
            
            2. **Update UI for Processing**:
               a. Call update_status() with progress message
               b. Message: "Opening browser..."
               c. Color: default (blue)
               d. disable_button: True (prevents double-click)
            
            3. **Try Browser Launch**:
               a. Enter try block for error handling
               
            4. **Build OAuth URL**:
               a. Set auth_url to Google OAuth endpoint:
                  "https://accounts.google.com/o/oauth2/v2/auth"
               b. Create params dictionary with OAuth parameters:
                  i. client_id: self.provider.client_id
                     (application identifier from Google Console)
                  ii. redirect_uri: self.provider.redirect_url
                      (where Google sends user after auth)
                  iii. response_type: 'code'
                       (authorization code flow, not implicit)
                  iv. scope: ' '.join(self.provider.scopes)
                      (space-separated list of requested permissions)
                  v. access_type: 'offline'
                     (request refresh token for long-term access)
                  vi. prompt: 'consent'
                      (force consent screen for consistent UX)
               c. URL-encode parameters: urllib.parse.urlencode(params)
               d. Build complete URL: f"{auth_url}?{encoded_params}"
               e. Store in oauth_url variable
            
            5. **Launch External Browser**:
               a. Call self.page.launch_url(oauth_url)
               b. Opens system browser to OAuth URL
               c. Non-blocking operation (returns immediately)
               d. User sees Google sign-in page in browser
            
            6. **Update UI with Instructions**:
               a. Call update_status() with instruction message
               b. Message: "Complete sign-in in browser, then return to app"
               c. Color: BLUE_600 (informational)
               d. disable_button: False (re-enable button)
               e. User can retry if browser doesn't open
            
            7. **Show Snackbar Notification**:
               a. Create SnackBar with content text
               b. Content: "Browser opening... Complete sign-in, then return here."
               c. Add action button: "OK"
               d. Assign to self.page.snack_bar
               e. Set snack_bar.open = True
               f. Call self.page.update() to display snackbar
               g. Provides additional visual feedback
            
            8. **Handle Exceptions**:
               a. Catch any Exception during browser launch
               b. Examples: URLError, OSError
               c. Call self.handle_error(ex, "Browser launch")
               d. Shows error message and re-enables button

        Interactions:
            - **urllib.parse.urlencode()**: Encodes OAuth parameters
            - **update_status()**: Shows progress and instructions
            - **ft.Page.launch_url()**: Opens external browser
            - **ft.SnackBar**: Shows notification about browser
            - **handle_error()**: Handles launch failures

        Example:
            >>> # Successful mobile login initiation
            >>> login._handle_mobile_login()
            >>> # Status: "Opening browser..." (blue, button disabled)
            >>> # Browser opens: accounts.google.com OAuth page
            >>> # Status: "Complete sign-in in browser..." (blue, button enabled)
            >>> # Snackbar: "Browser opening..."
            >>> # User completes OAuth in browser
            >>> # Browser redirects to external callback URL
            >>> # External handler processes token
            >>> # User manually returns to app
            >>> 
            >>> # Browser launch failure
            >>> login._handle_mobile_login()
            >>> # Status: "Opening browser..."
            >>> # Exception raised (no browser available)
            >>> # Status: "Browser launch failed: ..." (red, button enabled)
            >>> # User can retry

        See Also:
            - :meth:`handle_login`: Routes to this for mobile platforms
            - :class:`~src.ui.firebase_mobile_login.FirebaseMobileLogin`: 
              Alternative with polling
            - :meth:`handle_error`: Called on exceptions
            - :mod:`urllib.parse`: URL encoding utilities

        Notes:
            - Uses authorization code flow (not implicit grant)
            - Requires external callback URL handling
            - Browser opens asynchronously (non-blocking)
            - User must return to app manually after auth
            - Redirect URL must be configured in Google Console
            - Token exchange handled externally (not in app)
            - No automatic token retrieval (unlike desktop flow)
            - access_type='offline' requests refresh token
            - prompt='consent' shows consent screen every time
            - Snackbar provides additional user guidance
            - Button re-enabled to allow retry if needed
        """
        import urllib.parse
        
        self.update_status("Opening browser...", disable_button=True)
        
        try:
            auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
            params = {
                'client_id': self.provider.client_id,
                'redirect_uri': self.provider.redirect_url,
                'response_type': 'code',
                'scope': ' '.join(self.provider.scopes),
                'access_type': 'offline',
                'prompt': 'consent'
            }
            
            oauth_url = f"{auth_url}?{urllib.parse.urlencode(params)}"
            
            self.page.launch_url(oauth_url)
            
            self.update_status("Complete sign-in in browser, then return to app", ft.Colors.BLUE_600, False)

            show_snackbar(self.page, "Browser opened. Complete sign-in, then return here.", ft.Colors.BLUE_600)

        except Exception as ex:
            self.handle_error(ex, "Browser launch")