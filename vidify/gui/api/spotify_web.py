"""
Custom API implementation to ask the user for the Spotify Web credentials.
"""

import logging
from typing import Optional
from threading import Thread
from urllib.parse import urlparse
import webbrowser

from qtpy.QtCore import QSize, Qt, Signal
from qtpy.QtWidgets import QHBoxLayout, QLabel, QWidget
import tekore as tk
from flask import Flask, request

from vidify.gui import COLORS, FONTS
from vidify.config import Config


class SpotifyWebAuthenticator(QWidget):
    """
    This class is the main component in the Spotify Web Authenticator. It will
    follow the required protocol and emit the `done` signal once it's done.

    The authenticator will try to reuse credentials from previous attempts. If
    that fails, the usual procedure takes place:

    1. A server is started in the background. This will make it easier to obtain
       the authorization code. Otherwise, the user would have to copy-paste the
       resulting URL into this application. With a server, this is automatic.
    2. The PKCE authentication flow is followed by using the configured client
       credentials.
    3. The credentials are sent to Spotify in order to authenticate. The results
       will be sent to the server.
    4. If the previous step was successful, the server is shut down, and the
       `done` signal is emitted with the obtained token. Otherwise, back to step
       two.
    """

    done = Signal(tk.RefreshingToken)

    SCOPES = tk.scope.user_read_currently_playing

    # TODO: save credentials on success
    def __init__(self, config: Config) -> None:
        super().__init__()

        self._config = config

        # Setting up the layout
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        # Configuring the credentials for the auth process
        self._creds = tk.RefreshingCredentials(
            client_id=self._config.client_id,
            redirect_uri=self._config.redirect_uri,
        )

        # Trying to use previous credentials
        token = self._try_refresh_token()
        if token is not None:
            self.done.emit(token)
            return

        # Otherwise, starting the auth flow from scratch
        self._start_auth()

    def _try_refresh_token(self) -> Optional[tk.RefreshingToken]:
        """
        Tries to generate a self-refreshing token from the config.

        The authentication token itself isn't even saved in the config because
        it expires in an hour. Instead, the refresh token is used to generate a
        new token whenever the app is launched.
        """

        logging.info("Trying to refresh token")

        # Checking that the required credentials are valid before performing a
        # request.
        creds = {
            "client_id": self._config.client_id,
            "refresh_token": self._config.refresh_token,
        }
        for name, cred in creds.items():
            if cred in (None, ""):
                logging.info("Skipping: %s is empty", name)
                return

        # TODO: pretty error handling
        try:
            # Generating a RefreshingToken with the parameters
            return tk.refresh_pkce_token(**creds)
        except tk.HTTPError as e:
            print(f"Failed to refresh token: {e}")

    def _start_auth(self) -> None:
        # TODO: show message to user

        # Start the authentication server in the background
        self.server = Flask(
            "vidify_auth",
            template_folder="res/web/templates",
            static_folder="res/web/static"
        )
        self.server.add_url_rule("/callback/", view_func=self._auth_callback, methods=["GET"])
        self.server_thread = Thread(target=self._auth_server)
        self.server_thread.daemon = True
        self.server_thread.start()

        # Open auth URL in the browser. The verifier is saved to request the
        # token later on.
        url, verifier = self._creds.pkce_user_authorisation(self.SCOPES)
        self._verifier = verifier
        webbrowser.open_new(url)

    def _auth_server(self) -> None:
        """
        Thread in which the Flask server is ran in the background.
        """

        uri = urlparse(self._config.redirect_uri)
        if uri.hostname is None:
            raise Exception("Invalid redirect URI: no hostname specified")
        if uri.port is None:
            raise Exception("Invalid redirect URI: no port specified")

        logging.info("Starting web server at %s:%d", uri.hostname, uri.port)
        self.server.run(uri.hostname, uri.port, debug=False)

    def _auth_callback(self) -> None:
        """
        Called by the Spotify API upon successful authentication with the code.
        """

        code = request.args.get('code', None)
        # TODO: how to check state?
        # state = request.args.get('state', None)

        # TODO: pretty error handling (HTML)
        try:
            token = self._creds.request_pkce_token(code, self._verifier)
        except tk.HTTPError as e:
            print(f"Unable to obtain token: {e}")
            return f'error: {e}'

        # The authentication process is done. We save the refresh token for a
        # future attempt.
        logging.info("Successfully obtained acess token")
        self._config.refresh_token = token.refresh_token
        self.done.emit(token)

        # TODO: add template with prettier HTML
        return 'success!'
