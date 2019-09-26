import re
import time
from typing import Tuple, Callable


class ConnectionNotReady(Exception):
    """
    This error is called when no Spotify session is open or when
    no songs are currently playing, since it is better to catch them
    outside of the init function.
    """

    pass


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

    regex = "(.+?)(?:(?:: )|(?: : )|(?: - ))(.+)"
    match = re.match(regex, title)

    if match is not None:
        if None not in (match.group(1), match.group(2)):
            return match.group(1), match.group(2)

    return '', title


def wait_for_connection(connect: Callable, msg: str,
                        attempts: int = 30) -> bool:
    """
    Waits for a Spotify session to be opened or for a song to play.
    Times out after `attempts` seconds to avoid infinite loops or
    too many API/process requests.

    Returns True if the connection was succesfull and False otherwise.
    """

    counter = 0
    while counter < attempts:
        try:
            connect()
        except ConnectionNotReady:
            if counter == 0:
                print(msg)
            counter += 1
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break
        else:
            return True
    else:
        print("Timed out")

    return False
