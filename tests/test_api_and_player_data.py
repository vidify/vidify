"""
Tests for consistency in the data structures for both the APIs and the
players. This makes sure that their parameters are valid and consistent
throughout the entire module.
"""

import unittest

import qtpy.QtWebEngineWidgets  # noqa: F401
from qtpy.QtWidgets import QApplication

from vidify.gui.window import MainWindow
from vidify.api import APIS
from vidify.player import PLAYERS, initialize_player
from vidify.config import Config, OPTIONS


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
            self.assertEqual(api.id, api.id.upper())
            self.assertTrue(api.id not in existing_apis)
            existing_apis.append(api.id)

        existing_players = []
        for player in PLAYERS:
            self.assertEqual(player.id, player.id.upper())
            self.assertTrue(player.id not in existing_players)
            existing_players.append(player.id)

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

    def test_event_loop_interval(self):
        """
        Checking that the event intervals in APIData are valid (higher than
        100 milliseconds at least). Rather than 0, None should be used to
        specify that no event loops are used. A very low refresh rate would
        also cause lag in some systems.
        """

        for api in APIS:
            if api.event_loop_interval is not None:
                self.assertTrue(api.event_loop_interval > 100)

    def test_player_flags_name_exists(self):
        """
        Checking that the config options listed in the PlayerData structure
        holds real entries in Config.
        """

        for player in PLAYERS:
            for attr in player.flags:
                # Will raise AtributeError if it isn't found
                OPTIONS[attr]

    def test_gui_init_exists(self):
        """
        Checking that all the functions mentioned inside the APIData structures
        exist inside the GUI module.
        """

        for api in APIS:
            if api.gui_init_fn is not None:
                getattr(win, api.gui_init_fn)


if __name__ == '__main__':
    unittest.main()
