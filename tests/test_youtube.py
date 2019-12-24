import unittest

from vidify.youtube import YouTube, VideoNotFoundError


youtube = YouTube()


class TestYoutube(unittest.TestCase):
    def test_empty_data(self):
        """
        Checks that when the provided title and artist are empty,
        a VideoNotFoundError is raised.
        """

        with self.assertRaises(VideoNotFoundError):
            youtube.get_url(None, None)
        with self.assertRaises(VideoNotFoundError):
            youtube.get_url(None, '')
        with self.assertRaises(VideoNotFoundError):
            youtube.get_url('', None)
        with self.assertRaises(VideoNotFoundError):
            youtube.get_url('', '')

    def test_video_not_found(self):
        """
        Checks that when the provided video isn't found, a VideoNotFoundError
        is raised. The test is seemingly crappy but there's no other way to get
        YouTube-dl to fail, apart from disconnecting the computer's internet.
        """

        with self.assertRaises(VideoNotFoundError):
            youtube.get_url(
                "Hopefully this video name doesn't appear as a YouTube video"
                " \"result because the title\" is \"too long.\"",
                "I don't really have another way to test this but I'm going to"
                " keep typing gibberish until it's long enough. Lorem ipsum "
                " dxxxxxxxxxxxxxxxxxxxxxxxxxxxdipiscing elit. Nam consectetur"
                " ax xx x   x xxxx xxxx    x xahasellus sodales, lectus in"
                " px xx x xxx xxxx xxxx xx x xarius metus, posuere pharetra"
                " ux    x   x xxxx xxxx xx x xrerdum pharetra lacus et"
                " ex xx x xxx xxxx xxxx xx xxxullus. Ut a imperdiet tortor."
                " Cx xx x   x    x    x    x xfeget bibendum nisi. Donec"
                " axxxxxxxxxxxxxxxxxxxxxxxxxxxsanec efficitur urna accumsan.")

if __name__ == '__main__':
    unittest.main()
