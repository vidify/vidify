import os
import sys
import unittest
import unittest.mock
import configparser

from vidify.config import Options, Config


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
            self.config.parse(config_file=TEST_PATH)

    def tearDown(self):
        try:
            os.remove(TEST_PATH)
        except FileNotFoundError:
            pass
        else:
            print("Removed dummy config file")

    def test_order(self):
        """
        The order should always be:
        __setattr__ > arguments > config file > defaults
        """

        attr = 'vlc_args'
        arg = '--vlc-args'
        section = getattr(Options, attr).section

        # Default
        with unittest.mock.patch('sys.argv', ['']):
            self.config.parse(TEST_PATH)
        true_value = getattr(Options, attr).default
        conf_value = getattr(self.config, attr)
        self.assertEqual(conf_value, true_value)

        # Config file
        true_value = 'file'
        self.config.write_file(section, attr, true_value)
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

        # __setattr__
        true_value = '__setattr__'
        setattr(self.config, attr, true_value)
        conf_value = getattr(self.config, attr)
        self.assertEqual(conf_value, true_value)

        # Arguments again (without changing true_value from now on, since
        # it should stay the same as the last one with __setattr__)
        invalid_value = "not_this_value"
        args = [sys.argv[0], f"{arg}={invalid_value}"]
        with unittest.mock.patch('sys.argv', args):
            self.config.parse(TEST_PATH)
        conf_value = getattr(self.config, attr)
        self.assertEqual(conf_value, true_value)

        # Config file again. Same as above.
        self.config.write_file(section, attr, invalid_value)
        with unittest.mock.patch('sys.argv', ['']):
            self.config.parse(TEST_PATH)
        conf_value = getattr(self.config, attr)
        self.assertEqual(conf_value, true_value)

    def test_arguments_and_options_consistency(self):
        """
        Makes sure that all arguments in the options are equivalent to their
        name in the config file. This is not done automatically in the config
        file to simplify it, but it should be checked.
        """

        for option in Options:
            # Not all options are arguments
            if option.args is None:
                continue

            # Checking the number of arguments
            self.assertTrue(len(option.args) > 0)
            self.assertTrue(len(option.args) <= 2)

            # Arguments formatting is valid
            if len(option.args) == 2:
                self.assertTrue(option.args[0].startswith('-'))
            self.assertTrue(option.args[len(option.args) - 1].startswith('--'))

            # Consistency with the arguments: converting it to an option:
            # --vlc-args -> vlc_args. If 'store_false' is used, it should
            # have a `no` as the prefix to indicate it.
            opt = option.name
            arg = option.args[len(option.args) - 1]
            arg = arg[2:]
            arg = arg.replace('-', '_')
            if option.arg_action == 'store_false':
                arg = 'no_' + arg
            self.assertEqual(opt, option.name)

            # If it's an argument, the description and arg_action shouldn't be
            # empty
            self.assertNotIsInstance(option.description, type(None))
            self.assertNotEqual(option.description, '')
            self.assertNotIsInstance(option.arg_action, type(None))
            self.assertNotEqual(option.arg_action, '')

    def test_argument_actions(self):
        """
        Makes sure that the argument actions make sense.
        """

        for option in Options:
            # Not all options are arguments
            if option.args is None:
                continue

            # store_true and store_false should be of type boolean
            if option.arg_action in ('store_true', 'store_false'):
                self.assertEqual(option.type, bool)

    def test_option_defaults(self):
        """
        Checks that the default value is of the type indicated as the default
        or None.
        """

        for option in Options:
            # Some options don't have a default
            if option.default is None:
                continue

            self.assertIsInstance(option.default, option.type)

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

    def test_default_returned(self):
        """
        Checking that the default value is returned when the value doesn't
        exist, rather than None. This will create the following empty field:

        [Defaults]
        lyrics =

        Here `lyrics` should be True instead of None, because the value
        inside the file was None and it used the default value instead.
        One test is done for each type of variable: bool, int and str.
        """

        for opt in Options:
            with open(self.config._path, 'w') as configfile:
                configfile.write(f"[Defaults]\n{opt.name} =\n")
            value = getattr(self.config, opt.name)
            true_value = opt.default
            self.assertEqual(value, true_value)

    def test_types_written(self):
        """
        __setattr__ may behave unexpectedly when writing files with types
        other than str. This makes sure no errors are raised when doing so.
        """

        variables = {
            'debug': True,
            'width': 22,
            'vlc_args': 'test',
            'lyrics': None,
            'height': None,
            'mpv_flags': None
        }

        # Checking that the values are the same as the ones set.
        for name, real_value in variables.items():
            setattr(self.config, name, real_value)
            conf_value = getattr(self.config, name)
            self.assertEqual(conf_value, real_value)


if __name__ == '__main__':
    unittest.main()
