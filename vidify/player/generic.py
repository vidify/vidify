"""
Generic implementation of a player that can be used in this app.
"""


from abc import ABCMeta, abstractmethod
from qtpy.QtWidgets import QFrame


class PlayerBase(QFrame):
    __metaclass__ = ABCMeta
    """
    The abstract base class used for any player in this app.

    Other notes:
        * The player's module should have an entry in the list of supported
        players in vidify.player (the __init__.py file).
        * The player itself must inherit from `QFrame`.
        * The player should have a defined __init__ method to initialize the
        player when an instance is created.
        * The player should have a defined __del__ method to terminate
        itself when the app is closed safely, if necessary.
        * The player module should have a docstring at the top with a brief
        introduction to the player, and a reminder to check this file for more
        information about the player modules.
    """

    @property
    @abstractmethod
    def pause(self) -> bool:
        """
        Returns the current status of the player as a boolean. True means the
        player is paused, and False means it's currently playing.
        """

    @pause.setter
    @abstractmethod
    def pause(self, do_pause: bool) -> None:
        """
        The video will be paused if `do_pause` is True, or will be played if
        it's False. If `do_pause` is already in the requested status, nothing
        should be done.

        It's used this way because it's more versatile: a boolean can be
        provided instead of using play() or pause(), making sure the player
        does what it's told.
        """

    @property
    @abstractmethod
    def position(self) -> int:
        """
        Returns the position of the player in milliseconds.
        """

    @position.setter
    @abstractmethod
    def position(self, ms: int) -> None:
        """
        Sets the player's position in milliseconds.

        If the player can end up in an undefined behavior due to modifying
        the position when the video hasn't loaded yet, this function should
        block until it's possible to do so.
        """

    @abstractmethod
    def start_video(self, media: str, is_playing: bool = True) -> None:
        """
        Starts a new video in the player. This doesn't mean the player it's
        initialized, since that's done in `__init__`. When this function is
        called, the player should be ready to start a new video.

        `media` can be either an URL or a location in the user's filesystem.
        There shouldn't be a difference when providing these 2 types of media.

        `is_playing` is an optional boolean that can be provided to make sure
        the video starts at that state (playing/paused). Its value is True
        by default, so that calling `start_video(media)` also plays the video
        automatically.
        """
