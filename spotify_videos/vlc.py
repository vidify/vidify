import sys

import vlc


class VLCWindow:
    def __init__(self, logger: 'logging.Logger', vlc_args: str = "",
            fullscreen: bool = False) -> None:
        """
        The VLC window is the instance where media should play.

        The logger is an instance from the logging module, configured
        to show debug or error messages.

        It includes functions to get information from the instance
        or to control the player.
        """

        self._logger = logger
        self._fullscreen = fullscreen

        # VLC Instance
        try:
            self._instance = vlc.Instance(vlc_args)
        except NameError:
            logger.error("ERROR: VLC is not installed")
            sys.exit(1)
        self._video_player = self._instance.media_player_new()

    # Plays/Pauses the VLC player
    def play(self) -> None:
        self._video_player.play()

    def pause(self) -> None:
        self._video_player.pause()

    def toggle_pause(self) -> None:
        if self._video_player.is_playing():
            self.pause()
        else:
            self.play()

    # Starts a new video on the VLC player
    def start_video(self, url: str) -> None:
        self._logger.info("Starting new video")
        # Media instance, sets fullscreen and mute
        media = self._instance.media_new(url)
        self._video_player.set_media(media)
        self._video_player.audio_set_mute(True)
        self._video_player.set_fullscreen(self._fullscreen)

    # Set the position of the VLC media playing in ms
    def set_position(self, ms: int) -> None:
        self._video_player.set_time(ms)

    # Get the position of the VLC media playing in ms
    def get_position(self) -> int:
        return self._video_player.get_time()

