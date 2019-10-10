import unittest

import PySide2

from spotivids.player.vlc import VLCPlayer
from spotivids.api.linux import DBusAPI


class DBusTest(unittest.TestCase):
    def setUp(self):
        super().setUp()

        # Creating the first app instance
        if isinstance(PySide2.QtGui.qApp, type(None)):
            self.app = PySide2.QtWidgets.QApplication([])
        else:
            self.app = PySide2.QtGui.qApp
        player = VLCPlayer()
        self.dbus = DBusAPI(player)

    def tearDown(self):
        del self.app
        return super().tearDown()

    def test_bool_status(self):
        self.assertFalse(self.dbus._bool_status("stopped"))
        self.assertFalse(self.dbus._bool_status("sToPPeD"))
        self.assertFalse(self.dbus._bool_status("paused"))
        self.assertFalse(self.dbus._bool_status("paUsEd"))
        self.assertTrue(self.dbus._bool_status("playing"))
        self.assertTrue(self.dbus._bool_status("Playing"))

    def test_format_metadata(self):
        metadata = {
            'xesam:artist': [''],
            'xesam:title': 'Rick Astley - Never Gonna Give You Up'
        }
        artist, title = self.dbus._format_metadata(metadata)
        self.assertTrue(artist == "Rick Astley"
                        and title == "Never Gonna Give You Up")

        metadata['xesam:title'] = "Rick Astley: Never Gonna Give You Up"
        artist, title = self.dbus._format_metadata(metadata)
        self.assertTrue(artist == "Rick Astley"
                        and title == "Never Gonna Give You Up")

        metadata['xesam:title'] = "Rick Astley : Never Gonna Give You Up"
        artist, title = self.dbus._format_metadata(metadata)
        self.assertTrue(artist == "Rick Astley"
                        and title == "Never Gonna Give You Up")

        metadata['xesam:title'] = "Rick Astley Never Gonna Give You Up"
        artist, title = self.dbus._format_metadata(metadata)
        self.assertTrue(artist == ""
                        and title == "Rick Astley Never Gonna Give You Up")

        metadata['xesam:title'] = "Rick - Astley - Never Gonna Give You Up"
        artist, title = self.dbus._format_metadata(metadata)
        self.assertTrue(artist == "Rick"
                        and title == "Astley - Never Gonna Give You Up")

        metadata['xesam:artist'][0] = "Rick Astley"
        metadata['xesam:title'] = "Never Gonna - Give You Up"
        artist, title = self.dbus._format_metadata(metadata)
        self.assertTrue(artist == "Rick Astley"
                        and title == "Never Gonna - Give You Up")


if __name__ == '__main__':
    unittest.main()
