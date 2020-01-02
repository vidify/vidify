import unittest

from vidify import format_name
from vidify.api import split_title


class TestUtils(unittest.TestCase):
    def test_split_title(self):
        """
        Testing the regex used to split songs into title and artist when
        the API doesn't provide them separately.
        """

        # These titles are expected to be correctly split
        real_artist = 'Rick Astley'
        real_title = 'Never Gonna Give You Up'
        titles = ('Rick Astley - Never Gonna Give You Up',
                  'Rick Astley: Never Gonna Give You Up',
                  'Rick Astley : Never Gonna Give You Up')
        for title in titles:
            artist, title = split_title(title)
            self.assertEqual(artist, real_artist)
            self.assertEqual(title, real_title)

        # A string without separator should return the same as the title.
        real_title = 'Rick Astley Never Gonna Give You Up'
        artist, title = split_title(real_title)
        self.assertEqual(title, real_title)

        # More than 1 delimiter shouldn't matter when splitting, and the split
        # should only be done once and at the first delimiter found.
        title = 'Rick Astley - Never : Gonna - Give You Up'
        real_artist = 'Rick Astley'
        real_title = 'Never : Gonna - Give You Up'
        artist, title = split_title(title)
        self.assertEqual(title, real_title)
        self.assertEqual(artist, real_artist)

    def test_format_name(self):
        """
        Simple test for the format_name function in vidify.__init__.
        """

        artist = "Rick Astley"
        title = "Never Gonna Give You Up"

        self.assertEqual(format_name(artist, title),
                         "Rick Astley - Never Gonna Give You Up")

        self.assertEqual(format_name(None, title), title)
        self.assertEqual(format_name('', title), title)

        self.assertEqual(format_name(artist, None), artist)
        self.assertEqual(format_name(artist, ''), artist)

        self.assertEqual(format_name(None, None), '')
        self.assertEqual(format_name(None, ''), '')
        self.assertEqual(format_name('', None), '')
        self.assertEqual(format_name('', ''), '')


if __name__ == '__main__':
    unittest.main()
