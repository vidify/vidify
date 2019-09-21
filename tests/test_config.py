import os
import unittest
import configparser

from spotify_videos.config import Config


# Using a dummy config file
path = 'test.ini'


class ConfigTest(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        else:
            print("Removed dummy config file")

        self.config.parse(path)

    def tearDown(self):
        os.remove(path)

    def test_order(self):
        """
        The order should always be arguments > config file > defaults
        """

        attr = 'vlc_args'
        arg = '--vlc-args'

        # Default
        self.config.parse(path)
        true_value = getattr(self.config._options, attr).default
        conf_value = getattr(self.config, attr)
        self.assertEqual(conf_value, true_value)

        # Config file
        true_value = 'file'
        self.config.write_config_file('Defaults', attr, true_value)
        self.config.parse(path)
        conf_value = getattr(self.config, attr)
        self.assertEqual(conf_value, true_value)

        # Arguments
        true_value = 'args'
        args = [arg, true_value]

        self.config.parse(path, args)
        conf_value = getattr(self.config, attr)
        self.assertEqual(conf_value, true_value)

    def test_write(self):
        """
        Check if the config file is modified correctly. The nonexisting
        section should be created too.
        """

        key = 'test_attr'
        section = 'Test'
        value = 'test_value'
        self.config.write_config_file(section, key, value)
        conf = configparser.ConfigParser()
        conf.read(path)
        self.assertEqual(conf[section][key], value)


if __name__ == '__main__':
    unittest.main()
