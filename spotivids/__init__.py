import os
import sys
import logging
from contextlib import contextmanager

from .config import Config


# Initialization and parsing of the config from arguments and config file
config = Config()
config.parse()

# Logger initialzation with precise milliseconds handler.
logger = logging.getLogger('spotivids')

handler = logging.StreamHandler()
formatter = logging.Formatter(
    "[%(asctime)s.%(msecs)03d] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S")
handler.setFormatter(formatter)
logger.addHandler(handler)

level = logging.DEBUG if config.debug else logging.ERROR
logger.setLevel(level)

# Useful global variables for cross-platform and utils
BSD = sys.platform.find('bsd') != -1
LINUX = sys.platform.startswith('linux')
MACOS = sys.platform.startswith('darwin')
WINDOWS = sys.platform.startswith('win')


@contextmanager
def stderr_redirected(to: str = os.devnull) -> None:
    """
    Redirecting stderr without leaks.
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
    Some local songs may not have an artist name so the formatting
    has to be different.
    """

    return title if artist in (None, '') else f"{artist} - {title}"
