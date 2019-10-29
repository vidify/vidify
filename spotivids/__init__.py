"""
This module has utilities used in different parts of the program, like the
logger, cross-platform variables...
"""

import os
import sys
from contextlib import contextmanager


# Useful global variables for cross-platform and utils
BSD = sys.platform.find('bsd') != -1
LINUX = sys.platform.startswith('linux')
MACOS = sys.platform.startswith('darwin')
WINDOWS = sys.platform.startswith('win')


@contextmanager
def stderr_redirected(to: str = os.devnull) -> None:
    """
    Redirecting stderr without leaks. This is used because sometimes VLC
    will print non-critical error messages even when told to be quiet.
    """

    fd = sys.stderr.fileno()

    def _redirect_stderr(to: str) -> None:
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


def format_name(artist: str, title: str) -> str:
    """
    Formatting the song name with the artist and title.

    Some local songs may not have an artist name so the formatting
    has to be different.
    """

    return title if artist in (None, '') else f"{artist} - {title}"
