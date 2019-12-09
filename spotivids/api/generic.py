"""
Generic implementation of the API module.
"""

from abc import ABC, abstractmethod
from typing import Tuple, Callable, Optional


class APIInitialize():
    # Custom message displayed when waiting for the API to be ready.
    connect_message: Optional[str]

    # The init function is called after connect() has been successful. This is
    # needed because connect() is executed asynchronously while displaying
    # the GUI.
    init: Callable[..., None]
    init_args: Tuple[any]

    # The event loop is started after the app has been launched. It checks for
    # changes in the API metadata asynchronously every `event_loop_interval`
    # milliseconds.
    event_loop: Callable[[], None]
    event_loop_interval: int


class APIBase(ABC):
    @property
    def artist(self):
        """
        """

    @property
    def title(self):
        """
        """

    @property
    def is_playing(self):
        """
        """

    @property
    def position(self):
        """
        """

    @abstractmethod
    def connect(self):
        """
        """

    @abstractmethod
    def event_loop(self):
        """
        """

    @abstractmethod
    def play_video(self):
        """
        """
