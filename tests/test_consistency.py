import unittest

from spotivids.api import APIData
from spotivids.player import PlayerData


class ConsistencyTest(unittest.TestCase):
    def test_uppercase_names(self):
        for api in APIData:
            self.assertEqual(api.name, api.name.upper())

        for player in PlayerData:
            self.assertEqual(player.name, player.name.upper())


if __name__ == '__main__':
    unittest.main()
