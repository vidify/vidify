"""
Tests for consistency in the data structures for both the APIs and the
players. This makes sure that their parameters are valid and consistent
throughout the entire module.
"""

import unittest

from qtpy.QtWidgets import QApplication

from vidify import CURRENT_PLATFORM, Platform
from vidify.gui.window import MainWindow
from vidify.api import APIData, get_api_data
from vidify.player import PlayerData, initialize_player
from vidify.config import Config, Options


config = Config()
config.parse()
app = QApplication(['vidify'])
win = MainWindow(config)


class DataStructuresTest(unittest.TestCase):
    def test_uppercase_names(self):
        """
        Checking that the names in the API and Player enumerations are all
        uppercase. This way, they are unique and can be searched easily with
        str.upper().
        """

        for api in APIData:
            self.assertEqual(api.name, api.name.upper())

        for player in PlayerData:
            self.assertEqual(player.name, player.name.upper())

    def test_imports_and_class_names_in_modules(self):
        """
        Checking that all the class names and modules listed in the APIData
        and Player structures exist.

        This is only done with the APIs supported by the current operating
        system though, so for a full coverage this test should be done on
        all supported platforms.
        """

        # The API has 2 different functions, one to obtain the APIData entry
        # (get_api_data), and another to initialize the API (initialize_api).
        # Both are tested this way.
        for api in APIData:
            if CURRENT_PLATFORM in api.platforms:
                win.initialize_api(get_api_data(api.name), do_start=False)

        for player in PlayerData:
            initialize_player(player.name, config)

        # Also checking that AttributeError is raised when an unexisting
        # player is provided.
        with self.assertRaises(AttributeError):
            initialize_player('player-does-not-exist', config)

        # If the API isn't found, KeyError should be raised.
        with self.assertRaises(KeyError):
            get_api_data('api-does-not-exist')

    def test_event_loop_interval(self):
        """
        Checking that the event intervals in APIData are valid (higher than
        100 milliseconds at least). Rather than 0, None should be used to
        specify that no event loops are used. A very low refresh rate would
        also cause lag in some systems.
        """

        for api in APIData:
            if api.event_loop_interval is not None:
                self.assertTrue(api.event_loop_interval > 100)

    def test_platforms(self):
        """
        Checking that all APIs have at least one available platform.
        """

        for api in APIData:
            self.assertTrue(len(api.platforms) > 0)
            # Also checking that the type is valid
            for p in api.platforms:
                self.assertIsInstance(p, Platform)

    def test_player_flags_name_exists(self):
        """
        Checking that the config options listed in the PlayerData structure
        holds real entries in Config.
        """

        for player in PlayerData:
            if player.config_flags_name is not None:
                getattr(Options, player.config_flags_name)

    def test_gui_init_exists(self):
        """
        Checking that all the functions mentioned inside the APIData structures
        exist inside the GUI module.
        """

        for api in APIData:
            if api.gui_init_fn is not None:
                # Will raise AtributeError if it isn't found
                getattr(win, api.gui_init_fn)


if __name__ == '__main__':
    unittest.main()
