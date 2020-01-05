"""
Simple module to obtain the lyrics of a song.

More sources other than LyricWikia could be implemented in the future. The
problem is that most require an API key and can be annoying to set up.
Other sources could be implemented with a web scrapper, but it's not reliable
enough. Lyricwikia is actually a scrapper but its lyrics are available for
free, in comparison to Genius.
"""

import lyricwikia

from vidify import format_name, Platform, CURRENT_PLATFORM


# The different error messages returned by LyricWikia in order to override
# them with the default error message.
ERROR_MESSAGES = (
    "Unfortunately, we are not licensed to display the full lyrics for this"
    " song at the moment. Hopefully we will be able to in the future. Until"
    " then... how about a random page?",)


def get_lyrics(artist: str, title: str) -> str:
    """
    Using lyricwikia to obtain the song lyrics.
    """

    name = format_name(artist, title)

    # Colors are not displayed on Windows because it doesn't support ANSI
    # escape codes and importing colorama isn't worth it currently.
    if CURRENT_PLATFORM == Platform.WINDOWS:
        name = f">> {name}\n"
    else:
        name = f"\033[4m{name}\033[0m\n"

    try:
        lyrics = lyricwikia.get_lyrics(artist, title) + "\n"
    except (lyricwikia.LyricsNotFound, AttributeError):
        lyrics = "No lyrics found\n"
    else:
        if lyrics in ERROR_MESSAGES:
            lyrics = "No lyrics found\n"

    return name + lyrics
