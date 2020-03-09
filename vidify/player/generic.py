"""
Generic implementation of a player that can be used in this app.
This describes the exact behaviour the players should have.
"""


from abc import ABCMeta, abstractmethod
from qtpy.QtWidgets import QFrame


class PlayerBase(QFrame):
    """
    The abstract base class used for any player in this app.

    Other notes:
        * The player's module should have an entry in the list of supported
        players in vidify.player (the __init__.py file).
        * The player module should have a docstring at the top with a brief
        introduction to the player, and a reminder to check this file for more
        information about the player modules.
    """

    __metaclass__ = ABCMeta

    # This boolean indicates if the player needs the direct link to the
    # YouTube video, or just the YouTube URL. By default it's true.
    DIRECT_URL = True

    @property
    @abstractmethod
    def pause(self) -> bool:
        """
        Returns the current status of the player as a boolean. True means the
        player is paused, and False means it's currently playing.

        Its behaviour is undefined if it's called before a video starts
        playing.
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

        Its behaviour is undefined if it's called before a video starts
        playing.
        """

    @property
    @abstractmethod
    def position(self) -> int:
        """
        Returns the position of the player in milliseconds.

        It may raise NotImplementedError if it's not possible to perform this
        action.

        Its behaviour is undefined if it's called before a video starts
        playing.
        """

    @abstractmethod
    def seek(self, ms: int, relative: bool = False) -> None:
        """
        Sets the player's position in milliseconds.

        If the player can end up in an undefined behavior due to modifying
        the position when the video hasn't loaded yet, this function should
        block until it's possible to do so.

        Since some players only have write access to the position (like the
        external), or have specific methods for relative, this method
        can't be a @property. It also allows to use the relative flag.

        If the absolute position has a negative value, it should use zero.

        Its behaviour is undefined if it's called before a video starts
        playing.
        """

    @abstractmethod
    def start_video(self, media: str, is_playing: bool = True) -> None:
        """
        Starts playing a new video.

        `media` can be either an URL or a location in the user's filesystem.
        There shouldn't be a difference when providing these 2 types of media.

        `is_playing` is an optional boolean that can be provided to make sure
        the video starts at that state (playing/paused). Its value is True
        by default, so that calling `start_video(media)` also plays the video
        automatically.
        """
