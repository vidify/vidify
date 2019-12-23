import os
import unittest

from spotivids import CURRENT_PLATFORM, Platform
from spotivids import Platform, CURRENT_PLATFORM


TRAVIS = "TRAVIS" in os.environ and os.environ["TRAVIS"] == "true"
SKIP_MSG = "Skipping this test as it won't work on the current system."


class SwSpotifyTest(unittest.TestCase):
    @unittest.skipIf(TRAVIS or CURRENT_PLATFORM not in (Platform.MACOS,
                     Platform.WINDOWS), SKIP_MSG)
    def test_simple(self):
        from spotivids.api.spotify.swspotify import SwSpotifyAPI
        api = SwSpotifyAPI()
        api.connect_api()
        api._refresh_metadata()
        api.event_loop()


if __name__ == '__main__':
    unittest.main()
