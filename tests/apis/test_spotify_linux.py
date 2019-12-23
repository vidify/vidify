import os
import unittest

from PySide2.QtWidgets import QApplication

from spotivids import CURRENT_PLATFORM, Platform
from spotivids.api.spotify.linux import SpotifyLinuxAPI

api = SpotifyLinuxAPI()
TRAVIS = "TRAVIS" in os.environ and os.environ["TRAVIS"] == "true"
SKIP_MSG = "Skipping this test as it won't work on the current system."


class SpotifyLinuxTest(unittest.TestCase):
    @unittest.skipIf(TRAVIS or CURRENT_PLATFORM not in (Platform.BSD,
                     Platform.LINUX), SKIP_MSG)
    def test_simple(self):
        from spotivids.api.spotify.linux import SpotifyLinuxAPI
        api = SpotifyLinuxAPI()
        api.connect_api()
        api._refresh_metadata()

    def test_bool_status(self):
        self.assertFalse(SpotifyLinuxAPI._bool_status("stopped"))
        self.assertFalse(SpotifyLinuxAPI._bool_status("sToPPeD"))
        self.assertFalse(SpotifyLinuxAPI._bool_status("paused"))
        self.assertFalse(SpotifyLinuxAPI._bool_status("paUsEd"))
        self.assertTrue(SpotifyLinuxAPI._bool_status("playing"))
        self.assertTrue(SpotifyLinuxAPI._bool_status("Playing"))


if __name__ == '__main__':
    unittest.main()
