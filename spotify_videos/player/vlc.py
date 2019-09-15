import logging

import vlc


class VLCPlayer(object):
    def __init__(self, logger: logging.Logger, vlc_args: str = "",
                 fullscreen: bool = False) -> None:
        """
        This VLC player is the instance where media should play.

        The logger is an instance from the logging module, configured
        to show debug or error messages.
        """

        self._logger = logger
        self._fullscreen = fullscreen

        # The config file might have an empty field for it
        if vlc_args is None:
            vlc_args = ""
        vlc_args += " --no-audio"
        if self._logger.level <= logging.INFO:
            vlc_args += " --verbose 1"
        else:
            vlc_args += " --quiet"

        try:
            self._vlc = vlc.Instance(vlc_args)
        except NameError:
            raise Exception("VLC is not installed")

        if self._vlc is None:
            raise AttributeError("VLC couldn't load. This is almost always"
                                 " caused by an unexistent parameter passed"
                                 " with --vlc-args")

        self._player = self._vlc.media_player_new()

    def play(self) -> None:
        self._logger.info("Playing video")
        self._player.play()

    def pause(self) -> None:
        self._logger.info("Pausing video")
        self._player.pause()

    def toggle_pause(self) -> None:
        if self._player.is_playing():
            self.pause()
        else:
            self.play()

    @property
    def position(self) -> int:
        """
        Getting the position of the VLC player in milliseconds
        """

        return self._player.get_time()

    @position.setter
    def position(self, ms: int) -> None:
        """
        Setting the position in milliseconds
        """

        self._logger.info(f"Time set to {ms} milliseconds")
        self._player.set_time(ms)

    def start_video(self, url: str, is_playing: bool = True) -> None:
        """
        Starts a new video in the VLC player. It can be directly played
        with `is_playing` to avoid extra calls.

        The fullscreen can't be set as an initial parameter so it's indicated
        when the video starts.
        """

        self._logger.info("Starting new video")
        media = self._vlc.media_new(url)
        self._player.set_media(media)
        self._player.set_fullscreen(self._fullscreen)
        if is_playing:
            self.play()
