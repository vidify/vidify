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
        print(lyricwikia.get_lyrics(artist, title) + "\n")
    except (lyricwikia.LyricsNotFound, AttributeError):
        print("No lyrics found\n")
