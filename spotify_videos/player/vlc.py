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

        try:
            self._vlc = vlc.Instance(vlc_args)
        except NameError:
            raise Exception("ERROR: VLC is not installed")
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
        from here to avoid extra calls.

        The audio is muted, which is needed because not all the youtube-dl
        videos are silent. The fullscreen is also set.
        """

        self._logger.info("Starting new video")
        media = self._vlc.media_new(url)
        self._player.set_media(media)
        self._player.audio_set_mute(True)
        self._player.set_fullscreen(self._fullscreen)
        if is_playing:
            self.play()