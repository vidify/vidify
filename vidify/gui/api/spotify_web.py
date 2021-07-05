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

    1. A server is started in the background.
    2. The user inputs their credentials.
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
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        token = self._try_refresh_token()
        if token is not None:
            self.done.emit(token)
            return

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

        # Generating a RefreshingToken with the parameters
        return tk.refresh_user_token(**creds)

    def _start_auth(self) -> None:
        # TODO: show message to user

        # Start the server in the background
        self.server = Flask(
            "vidify_auth",
            template_folder="res/web/templates",
            static_folder="res/web/static"
        )
        self.server.add_url_rule("/callback/", view_func=self._callback, methods=["GET"])
        self.server_thread = Thread(target=self._start_web_server)
        self.server_thread.daemon = True
        self.server_thread.start()

        # Setup credentials and open auth URL in the browser
        self.creds = tk.RefreshingCredentials(
            client_id=self._config.client_id,
            redirect_uri=self._config.redirect_uri,
        )
        url = self.creds.user_authorisation_url(self.SCOPES)
        webbrowser.open_new(url)

    def _start_web_server(self) -> None:
        uri = urlparse(self._config.redirect_uri)
        if uri.hostname is None:
            raise Exception("Invalid redirect URI: no hostname specified")
        if uri.port is None:
            raise Exception("Invalid redirect URI: no port specified")

        logging.info("Starting web server at %s:%d", uri.hostname, uri.port)
        self.server.run(uri.hostname, uri.port, debug=False)

    def _callback(self) -> None:
        # TODO: add template with prettier HTML
        code = request.args.get('code', None)
        # state = request.args.get('state', None)
        # auth = auths.pop(state, None)

        # token = auth.request_token(code, state)
        return f"code {code}"

    def save_config(self):
        """
        The obtained credentials are saved for the future
        """

        logging.info("Saving the Spotify Web API credentials")
        self.config.client_secret = self._spotify_web_prompt.client_secret
        self.config.client_id = self._spotify_web_prompt.client_id
        self.config.refresh_token = token.refresh_token
