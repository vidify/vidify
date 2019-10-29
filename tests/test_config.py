import os
import sys
import unittest
import unittest.mock
import configparser

from spotivids.config import Options, Config


# Using a dummy config file
TEST_PATH = 'test.ini'


class ConfigTest(unittest.TestCase):
    def setUp(self):
        super().setUp()

        # Empty arguments
        self.config = Config()
        try:
            os.remove(TEST_PATH)
        except FileNotFoundError:
            pass
        else:
            print("Removed dummy config file")

        with unittest.mock.patch('sys.argv', ['']):
            self.config.parse(config_path=TEST_PATH)

    def tearDown(self):
        os.remove(TEST_PATH)

    def test_order(self):
        """
        The order should always be arguments > config file > defaults
        """

        attr = 'vlc_args'
        arg = '--vlc-args'

        # Default
        with unittest.mock.patch('sys.argv', ['']):
            self.config.parse(TEST_PATH)
        true_value = getattr(Options, attr).default
        conf_value = getattr(self.config, attr)
        self.assertEqual(conf_value, true_value)

        # Config file
        true_value = 'file'
        setattr(self.config, attr, true_value)
        with unittest.mock.patch('sys.argv', ['']):
            self.config.parse(TEST_PATH)
        conf_value = getattr(self.config, attr)
        self.assertEqual(conf_value, true_value)

        # Arguments
        true_value = 'args'
        args = [sys.argv[0], f"{arg}={true_value}"]
        with unittest.mock.patch('sys.argv', args):
            self.config.parse(TEST_PATH)
        conf_value = getattr(self.config, attr)
        self.assertEqual(conf_value, true_value)

    def test_write(self):
        """
        Check if the config file is modified correctly.
        """

        # The non-existing section should be created with write_value
        key = 'test_attr'
        section = 'Test'
        true_value = 'test_value'
        self.config.write_file(section, key, true_value)
        # Checking the new value in the config file
        conf = configparser.ConfigParser()
        conf.read(TEST_PATH)
        value = conf[section][key]
        self.assertEqual(value, true_value)

        # With the __setattr__ implementation
        key = 'vlc_args'
        section = 'Defaults'
        true_value = 'test_value2'
        setattr(self.config, key, true_value)
        # Checking in the object
        value = getattr(self.config, key)
        self.assertEqual(value, true_value)
        # Checking in the file
        conf = configparser.ConfigParser()
        conf.read(TEST_PATH)
        self.assertEqual(conf[section][key], true_value)


if __name__ == '__main__':
    unittest.main()
