import os
import unittest
import unittest.mock

from PySide2.QtGui import qApp
from PySide2.QtWidgets import QApplication

from spotivids import BSD, LINUX, MACOS, WINDOWS
from spotivids.youtube import YouTube
from spotivids.player.vlc import VLCPlayer


TRAVIS = "TRAVIS" in os.environ and os.environ["TRAVIS"] == "true"
SKIP_MSG = "Skipping this test as it won't work on the current system."


class APITest(unittest.TestCase):
    """
    Really simple test to check for trivial errors in all platforms by
    running the module on the supported systems. They shouldn't be run
    by Travis or an unsupported OS.
    """

    def setUp(self):
        super().setUp()

        self.youtube = YouTube()
        # Creating the first app instance
        if isinstance(qApp, type(None)):
            self.app = QApplication([])
        else:
            self.app = qApp
        self.vlc = VLCPlayer()

        # What is this import doing here you may ask? A terrifying tale
        # of C locales and segfaults haunts this code. Too many programmers
        # have died in agonizing pain while trying to answer that. It is still
        # unknown to the human race to this day. For more details, visit:
        # https://github.com/mpv-player/mpv/issues/7102#issuecomment-547626491
        from spotivids.player.mpv import MpvPlayer
        self.mpv = MpvPlayer()

    def tearDown(self):
        del self.app
        return super().tearDown()

    @unittest.skipIf(TRAVIS or not (BSD or LINUX), SKIP_MSG)
    def test_dbus(self):
        # Format metadata, bool status are tested in test_dbus
        from spotivids.api.linux import DBusAPI
        for player in (self.vlc, self.mpv):
            dbus = DBusAPI(player, self.youtube)
            dbus.connect()
            dbus._refresh_metadata()
            dbus.play_video()
            dbus.disconnect()

    @unittest.skipIf(TRAVIS or not (MACOS or WINDOWS), SKIP_MSG)
    def test_swspotify(self):
        from spotivids.api.swspotify import SwSpotifyAPI
        for player in (self.vlc, self.mpv):
            swspotify = SwSpotifyAPI(player, self.youtube)
            swspotify.connect()
            swspotify._refresh_metadata()
            swspotify.play_video()
            swspotify.event_loop()

    @unittest.skipIf(TRAVIS, SKIP_MSG)
    def test_web(self):
        """
        The web credentials have to be already in the config file, including
        the auth token and the expiration date.
        """

        from spotivids.api.web import get_token, WebAPI
        from spotivids.config import Config
        config = Config()
        with unittest.mock.patch('sys.argv', ['']):
            config.parse()
        token = get_token(config.auth_token, config.refresh_token,
                          config.expiration, config.client_id,
                          config.client_secret, config.redirect_uri)
        web = WebAPI(self.vlc, self.youtube, token)
        web.connect()
        web._refresh_metadata()
        web.play_video()
        web.event_loop()


if __name__ == '__main__':
    unittest.main()
