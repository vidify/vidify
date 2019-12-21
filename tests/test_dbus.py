import unittest

from PySide2.QtWidgets import QApplication

from spotivids.api.spotify.linux import SpotifyLinuxAPI

API = SpotifyLinuxAPI()


class DBusTest(unittest.TestCase):
    def test_bool_status(self):
        self.assertFalse(API._bool_status("stopped"))
        self.assertFalse(API._bool_status("sToPPeD"))
        self.assertFalse(API._bool_status("paused"))
        self.assertFalse(API._bool_status("paUsEd"))
        self.assertTrue(API._bool_status("playing"))
        self.assertTrue(API._bool_status("Playing"))

    def test_format_metadata(self):
        metadata = {
            'xesam:artist': [''],
            'xesam:title': 'Rick Astley - Never Gonna Give You Up'
        }
        artist, title = API._format_metadata(metadata)
        self.assertTrue(artist == "Rick Astley"
                        and title == "Never Gonna Give You Up")

        metadata['xesam:title'] = "Rick Astley: Never Gonna Give You Up"
        artist, title = API._format_metadata(metadata)
        self.assertTrue(artist == "Rick Astley"
                        and title == "Never Gonna Give You Up")

        metadata['xesam:title'] = "Rick Astley : Never Gonna Give You Up"
        artist, title = API._format_metadata(metadata)
        self.assertTrue(artist == "Rick Astley"
                        and title == "Never Gonna Give You Up")

        metadata['xesam:title'] = "Rick Astley Never Gonna Give You Up"
        artist, title = API._format_metadata(metadata)
        self.assertTrue(artist == ""
                        and title == "Rick Astley Never Gonna Give You Up")

        metadata['xesam:title'] = "Rick - Astley - Never Gonna Give You Up"
        artist, title = API._format_metadata(metadata)
        self.assertTrue(artist == "Rick"
                        and title == "Astley - Never Gonna Give You Up")

        metadata['xesam:artist'][0] = "Rick Astley"
        metadata['xesam:title'] = "Never Gonna - Give You Up"
        artist, title = API._format_metadata(metadata)
        self.assertTrue(artist == "Rick Astley"
                        and title == "Never Gonna - Give You Up")


if __name__ == '__main__':
    unittest.main()
