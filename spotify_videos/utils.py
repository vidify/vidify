import re
import os
import sys
from typing import Tuple
from contextlib import contextmanager

"""
The utils module contains functions that can be used from
both player classes and some other generic utilities
"""


SPLIT_ARTIST_REGEX = "(.+?)(?:(?:: )|(?: : )|(?: - ))(.+)"


def split_title(title: str) -> Tuple[str, str]:
    """
    Some local songs don't have an artist, so they are attempted
    to be split from the title manually with regex.

    The return is a tuple, with the order being: artist, title.

    The regex works with the following structures:
        Rick Astley - Never Gonna Give You Up
        Rick Astley: Never Gonna Give You Up
        Rick Astley : Never Gonna Give You Up
    """

    match = re.match(SPLIT_ARTIST_REGEX, title)
    if match is not None:
        if None not in (match.group(1), match.group(2)):
            return match.group(1), match.group(2)

    return "", title


class ConnectionNotReady(Exception):
    """
    This error is called when no Spotify session is open or when
    no songs are currently playing, since it is better to catch them
    outside of the init function.
    """

    pass


@contextmanager
def stderr_redirected(to: str = os.devnull) -> None:
    """
    Redirecting stderr without leaks.
    """

    fd = sys.stderr.fileno()

    def _redirect_stderr(to):
        sys.stderr.close()  # + implicit flush()
        os.dup2(to.fileno(), fd)  # fd writes to 'to' file
        sys.stderr = os.fdopen(fd, 'w')  # Python writes to fd

    with os.fdopen(os.dup(fd), 'w') as old_stderr:
        with open(to, 'w') as file:
            _redirect_stderr(to=file)
        try:
            # Allow code to be run with the redirected stderr
            yield
        finally:
            # Restore stderr. Some flags may change
            _redirect_stderr(to=old_stderr)
