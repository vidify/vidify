import unittest

from spotivids import BSD, LINUX, MACOS, WINDOWS
from spotivids.__main__ import choose_platform
from spotivids.player.vlc import VLCPlayer
from spotivids.player.mpv import MpvPlayer


vlc = VLCPlayer()
mpv = MpvPlayer()


class APITest(unittest.TestCase):
    """
    Simple test to check for simple errors in all platforms by running the
    module on the supported systems. It is run automatically with Travis, so
    manual interaction isn't expected.
    """

    def test_connection(self):
        choose_platform()

    def test_dbus(self):
        # This won't work on systems other than BSD or Linux
        if not (BSD or LINUX):
            return

        from spotivids.api.linux import DBusAPI
        for player in (vlc, mpv):
            dbus = DBusAPI(player)
            dbus.connect()
            # Format metadata and bool status are tested in test_dbus
            dbus._refresh_metadata()
            #  dbus._on_properties_changed()  # TODO
            dbus.disconnect()

    def test_swspotify(self):
        # This won't work on systems other than macOS or Windows
        if not (MACOS or WINDOWS):
            return

        from spotivids.api.swspotify import SwSpotifyAPI
        for player in (vlc, mpv):
            swspotify = SwSpotifyAPI(player)
            swspotify.connect()
            swspotify._refresh_metadata()
            swspotify.play_video()
            swspotify.event_loop()

    def test_web(self):
        """
        Client ID and Client Secret should be set up as environment variables.
        """

        from spotivids.api.web import WebAPI
        for player in (vlc, mpv):
            web = WebAPI(player)
            web.connect()
            position = web.position
            web._refresh_metadata()
            web.play_video()
            web.event_loop()
