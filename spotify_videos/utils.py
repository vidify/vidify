import re
import os
import sys
from contextlib import contextmanager


# Matches the following:
#     Rick Astley - Never Gonna Give You Up
#     Rick Astley: Never Gonna Give You Up
#     Rick Astley : Never Gonna Give You Up
SPLIT_ARTIST_REGEX = "(.+?)(?:(?:: )|(?: : )|(?: - ))(.+)"

# Some local songs don't have an artist, so they are
# tried to be split from the title manually with regex
# Return order is <artist>, <title>
def split_title(title):
    match = re.match(SPLIT_ARTIST_REGEX, title)
    if match is not None:
        if None not in (match.group(1), match.group(2)):
            return match.group(1), match.group(2)

    return "", title


# Redirecting/hiding stderr without leaks
@contextmanager
def stderr_redirected(to: str = os.devnull) -> None:
    fd = sys.stderr.fileno()

    def _redirect_stderr(to):
        sys.stderr.close() # + implicit flush()
        os.dup2(to.fileno(), fd) # fd writes to 'to' file
        sys.stderr = os.fdopen(fd, 'w') # Python writes to fd

    with os.fdopen(os.dup(fd), 'w') as old_stderr:
        with open(to, 'w') as file:
            _redirect_stderr(to=file)
        try:
            yield # Allow code to be run with the redirected stderr
        finally:
            _redirect_stderr(to=old_stderr) # Restore stderr. Some flags may change

