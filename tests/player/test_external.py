import time
import unittest

import qtpy.QtWebEngineWidgets  # noqa: F401
from qtpy.QtWidgets import QApplication

from vidify.player.external import ExternalPlayer


if QApplication.instance() is None:
    _ = QApplication(["vidify"])
p: ExternalPlayer = None
POS_MARGIN = 10  # In milliseconds


def pos_equal(p1: float, p2: float) -> bool:
    return p1 - POS_MARGIN < p2 and p1 + POS_MARGIN > p2


class ExternalPlayerTest(unittest.TestCase):
    def setUp(self):
        super().setUp()
        global p
        p = ExternalPlayer("test")

    def tearDown(self):
        global p
        del p
        super().tearDown()

    def test_is_playing(self):
        # Starting a new video and pausing it
        p.start_video("test", is_playing=True)
        self.assertFalse(p.pause)
        p.pause = True
        self.assertTrue(p.pause)

        # Starting a new video paused and playing it
        p.start_video("test", is_playing=False)
        self.assertTrue(p.pause)
        p.pause = False
        self.assertFalse(p.pause)

        # Starting a new video should change is_playing, too.
        p.pause = True
        p.start_video("test", is_playing=True)
        self.assertFalse(p.pause)

        p.pause = False
        p.start_video("test", is_playing=False)
        self.assertTrue(p.pause)

        p.pause = False
        p.start_video("test", is_playing=True)
        self.assertFalse(p.pause)

        p.pause = True
        p.start_video("test", is_playing=False)
        self.assertTrue(p.pause)

    def test_position_change(self):
        """
        The position is internally calculated in the external player. It's a
        bit confusing, so it has to be tested thoroughly.

        The player's position can't be known exactly, so it's compared with
        a margin.
        """

        def test_manual_change(relative: bool):
            # Modifying the position manually. No time is elapsed inside
            # this function, so the results should be the same when the video
            # starts paused or playing.
            p.start_video("test")
            p.seek(0, relative=False)
            self.assertTrue(pos_equal(0, p.position))
            p.seek(-1000, relative=False)
            self.assertTrue(pos_equal(0, p.position))
            p.seek(1000, relative=False)
            self.assertTrue(pos_equal(1000, p.position))
            p.seek(1000, relative=True)
            self.assertTrue(pos_equal(2000, p.position))
            p.seek(-500, relative=True)
            self.assertTrue(pos_equal(1500, p.position))
            p.seek(-5000, relative=True)
            self.assertTrue(pos_equal(0, p.position))

        test_manual_change(False)
        test_manual_change(True)

    def test_position_with_sleep(self):
        p.start_video("test")
        # Time passing should modify the position
        p.seek(0, relative=False)
        time.sleep(0.25)
        self.assertTrue(pos_equal(250, p.position))
        # Only if it's not paused
        p.pause = True
        time.sleep(0.2)
        self.assertTrue(pos_equal(250, p.position))

    def test_position_new_videos(self):
        # Playing new videos
        # If it starts paused, it shouldn't be modified
        p.start_video("test", is_playing=False)
        time.sleep(0.1)
        self.assertTrue(pos_equal(0, p.position))
        # If it starts playing, it should act as usual
        p.start_video("test", is_playing=True)
        time.sleep(0.3)
        self.assertTrue(pos_equal(300, p.position))
        # Same if it was paused before starting
        p.pause = True
        p.start_video("test", is_playing=False)
        time.sleep(0.1)
        self.assertTrue(pos_equal(0, p.position))


if __name__ == '__main__':
    unittest.main()
