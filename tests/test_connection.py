import unittest

from spotivids.__main__ import choose_platform
from spotivids.player.vlc import VLCPlayer
from spotivids.player.mpv import MpvPlayer
from spotivids.api.linux import DBusAPI
from spotivids.api.swspotify import SwSpotifyAPI
from spotivids.api.web import WebAPI


# TODO: Finish tests, test play_videos_xxx too.


class ConnectionTest(unittest.TestCase):
    """
    Simple test to check for simple errors in all platforms by running the
    module on the supported systems. It is run automatically with Travis, so
    manual interaction isn't expected.
    """

    def setUp(self):
        self.vlc = VLCPlayer()
        self.mpv = MpvPlayer()

    def test_connection(self):
        choose_platform()

    def test_dbus(self):
        for player in (self.vlc, self.mpv):
            dbus = DBusAPI(player)
            dbus.connect()
            dbus._format_metadata()
            dbus._refresh_metadata()
            dbus._bool_status()
            dbus._on_properties_changed()
            dbus.disconnect()

    def test_swspotify(self):
        for player in (self.vlc, self.mpv):
            swspotify = SwSpotifyAPI(player)
            swspotify.connect()
            swspotify._refresh_metadata()
            swspotify._on_properties_changed()

    def test_web(self):
        """
        Client ID and Client Secret should be set up as environment variables.
        """

        for player in (self.vlc, self.mpv):
            web = WebAPI(player)
            web.connect()
            position = web.position
            web._refresh_metadata()
            web._on_properties_changed()
