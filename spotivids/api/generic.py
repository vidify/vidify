"""
Generic implementation of the API module.
"""

from abc import ABCMeta, abstractmethod
from typing import Tuple, Callable, Optional

from spotivids.player.generic import PlayerBase


class APIBase:
    __metaclass__ = ABCMeta

    """
    The abstract base class used for any API in this app. The API is defined
    as an object that can provide information about the status of the player
    

    Other notes:
        * The API's module should have an entry in the list of supported APIs
        in spotivids.api (the __init__.py file).
        * The API's __init__ function mustn't be blocking, since it's handled
        by the GUI.
        * The API module should have a docstring at the top introducing the
        API, and with a reminder to check this module for more information
        in general about the API implementations.
    """

    @property
    @abstractmethod
    def artist(self) -> str:
        """
        Returns the artist of the currently playing song.

        If it has more than one artist, the most relevant one (or just the
        first one) should be returned.
        """

    @property
    @abstractmethod
    def title(self) -> str:
        """
        Returns the title of the currently playing song.
        """

    @property
    @abstractmethod
    def is_playing(self) -> bool:
        """
        Returns a boolean that indicates whether the song is playing at that
        moment or not (as in being paused).
        """

    @property
    @abstractmethod
    def position(self) -> int:
        """
        Returns the position in milliseconds of the currently playing song.

        If the API can't implement this, `NotImplementedError` should be raised
        instead.
        """

    @abstractmethod
    def connect(self):
        """
        Initializes the connection with the API.

        A `ConnectionNotReady` exception should be raised if the attempt to
        connect didn't succeed. For example, if the player isn't open or if no
        songs are playing at that moment. This means that this function
        shouldn't block while waiting for the API to be ready.
        """

    @abstractmethod
    def event_loop(self):
        """
        Runs an iteration of the event loop.

        The event loop is a function that can be run periodically to check
        for updates in the API's metadata and act accordingly (start a new
        video, pause it, etc).

        This method may not be needed in some APIs, which should raise
        `NotImplementedError` instead. This information is saved in the API
        entry inside the API list so that the event loop isn't called.
        """

    @abstractmethod
    def play_video(self):
        """
        Plays a video in the API's player.

        connect() has to be used before this method in order to establish a
        connection with the API.
        """
