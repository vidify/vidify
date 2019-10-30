"""
Simple module to obtain the lyrics of a song.

More sources other than lyricwikia could be implemented in the future. The
problem is that most require and API key and it's not worth it. Other sources
can be implemented with a web scrapper, but it's not reliable enough.
Lyricwikia is actually a scrapper but its lyrics are available for free,
in comparison to Genius.
"""

import lyricwikia

from spotivids import format_name, WINDOWS


# The different error messages returned by lyricwikia
ERROR_MESSAGES = (
    "Unfortunately, we are not licensed to display the full lyrics for this"
    " song at the moment. Hopefully we will be able to in the future. Until"
    " then... how about a random page?")


def print_lyrics(artist: str, title: str) -> None:
    """
    Using lyricwikia to get lyrics.

    Colors are not displayed on Windows because it doesn't support ANSI
    escape codes and importing colorama isn't worth it currently.
    """

    name = format_name(artist, title)

    if WINDOWS:
        print(f">> {name}")
    else:
        print(f"\033[4m{name}\033[0m")

    try:
        msg = lyricwikia.get_lyrics(artist, title) + "\n"
    except (lyricwikia.LyricsNotFound, AttributeError):
        msg = "No lyrics found\n"

    if msg in ERROR_MESSAGES:
        msg = "No lyrics found\n"
    print(msg)
