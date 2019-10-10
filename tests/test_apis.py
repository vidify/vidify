import os
import unittest

import PySide2

from spotivids import BSD, LINUX, MACOS, WINDOWS
from spotivids.player.vlc import VLCPlayer
from spotivids.player.mpv import MpvPlayer


runningTravis = "TRAVIS" in os.environ and os.environ["TRAVIS"] == "true"
skipMsg = "Skipping this test as it won't work on the current system."


class APITest(unittest.TestCase):
    """
    Really simple test to check for trivial errors in all platforms by
    running the module on the supported systems. They shouldn't be run
    by Travis or an unsupported OS.
    """

    def setUp(self):
        super().setUp()

        # Creating the first app instance
        if isinstance(PySide2.QtGui.qApp, type(None)):
            self.app = PySide2.QtWidgets.QApplication([])
        else:
            self.app = PySide2.QtGui.qApp
        self.vlc = VLCPlayer()
        self.mpv = MpvPlayer()

    def tearDown(self):
        del self.app
        return super().tearDown()

    @unittest.skipIf(runningTravis or not (BSD or LINUX), skipMsg)
    def test_dbus(self):
        # Format metadata, bool status are tested in test_dbus
        from spotivids.api.linux import DBusAPI
        for player in (self.vlc, self.mpv):
            dbus = DBusAPI(player)
            dbus.connect()
            dbus._refresh_metadata()
            dbus.play_video()
            dbus.disconnect()

    @unittest.skipIf(runningTravis or not (MACOS or WINDOWS), skipMsg)
    def test_swspotify(self):
        from spotivids.api.swspotify import SwSpotifyAPI
        for player in (self.vlc, self.mpv):
            swspotify = SwSpotifyAPI(player)
            swspotify.connect()
            swspotify._refresh_metadata()
            swspotify.play_video()
            swspotify.event_loop()

    @unittest.skipIf(runningTravis, skipMsg)
    def test_web(self):
        """
        Client ID and Client Secret should be set up as environment variables.
        """

        from spotivids.api.web import WebAPI
        redirect_uri = "http://localhost:8888/callback/"
        web = WebAPI(self.vlc, redirect_uri=redirect_uri)
        web.connect()
        web._refresh_metadata()
        web.play_video()
        web.event_loop()


if __name__ == '__main__':
    unittest.main()
