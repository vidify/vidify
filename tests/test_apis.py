import os
import unittest
import unittest.mock

from PySide2.QtWidgets import QApplication

from spotivids import Platform, CURRENT_PLATFORM


TRAVIS = "TRAVIS" in os.environ and os.environ["TRAVIS"] == "true"
SKIP_MSG = "Skipping this test as it won't work on the current system."


class APITest(unittest.TestCase):
    """
    Really simple test to check for trivial errors in all platforms by
    running the module on the supported systems. They shouldn't be run
    by Travis or an unsupported OS.
    """

    @unittest.skipIf(TRAVIS or CURRENT_PLATFORM not in (Platform.BSD,
                     Platform.LINUX), SKIP_MSG)
    def test_dbus(self):
        # Format metadata, bool status are tested in test_dbus
        from spotivids.api.spotify.linux import SpotifyLinuxAPI
        api = SpotifyLinuxAPI()
        api.connect_api()
        api._refresh_metadata()

    @unittest.skipIf(TRAVIS or CURRENT_PLATFORM not in (Platform.MACOS,
                     Platform.WINDOWS), SKIP_MSG)
    def test_swspotify(self):
        from spotivids.api.spotify.swspotify import SwSpotifyAPI
        api = SwSpotifyAPI()
        api.connect_api()
        api._refresh_metadata()
        api.event_loop()

    @unittest.skipIf(TRAVIS, SKIP_MSG)
    def test_web(self):
        """
        The web credentials have to be already in the config file, including
        the auth token and the expiration date.
        """

        from spotivids.api.spotify.web import get_token, SpotifyWebAPI
        from spotivids.config import Config
        config = Config()
        with unittest.mock.patch('sys.argv', ['']):
            config.parse()
        token = get_token(config.auth_token, config.refresh_token,
                          config.expiration, config.client_id,
                          config.client_secret, config.redirect_uri)
        api = SpotifyWebAPI(token)
        api.connect_api()
        api._refresh_metadata()
        api.event_loop()


if __name__ == '__main__':
    unittest.main()
