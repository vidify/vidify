"""
Tests for consistency in the data structures for both the APIs and the
players. This makes sure that their parameters are valid and consistent
throughout the entire module.
"""

import unittest

from qtpy.QtWidgets import QApplication

from vidify.api import APIS
from vidify.core import Config
from vidify.gui.window import MainWindow
from vidify.player import PLAYERS, initialize_player

if QApplication.instance() is None:
    _ = QApplication(["vidify"])
config = Config()
config.parse()
win = MainWindow(config)


class DataStructuresTest(unittest.TestCase):
    def test_unique_uppercase_names(self):
        """
        Checking that the names in the API and Player enumerations are all
        unique and uppercase.
        """

        existing_apis = []
        for api in APIS:
            self.assertEqual(api.name, api.name.upper())
            self.assertTrue(api.name not in existing_apis)
            existing_apis.append(api.name)

        existing_players = []
        for player in PLAYERS:
            self.assertEqual(player.name, player.name.upper())
            self.assertTrue(player.name not in existing_players)
            existing_players.append(player.name)

    def test_imports_and_class_names_in_modules(self):
        """
        Checking that all the class names and modules listed in the APIData
        and Player structures exist.

        This is only done with the APIs supported by the current operating
        system though, so for a full coverage this test should be done on
        all supported platforms and with all the optional dependencies
        installed.
        """

        for api in APIS:
            if api.compatible and api.installed:
                win.initialize_api(api)

        for player in PLAYERS:
            if player.compatible and player.installed:
                initialize_player(player, config)

    def test_gui_init_exists(self):
        """
        Checking that all the functions mentioned inside the APIData structures
        exist inside the GUI module.
        """

        for api in APIS:
            if api.gui_init_fn is not None:
                getattr(win, api.gui_init_fn)


if __name__ == "__main__":
    unittest.main()
