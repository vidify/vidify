import sys

import vlc


class VLCPlayer:
    def __init__(self, logger: 'logging.Logger', vlc_args: str = "",
                 fullscreen: bool = False) -> None:
        """
        This VLC player is the VLC instance where media should play.

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
            raise Exception("ERROR: VLC is not installed")
        self._video_player = self._instance.media_player_new()

    def play(self) -> None:
        self._video_player.play()

    def pause(self) -> None:
        self._video_player.pause()

    def toggle_pause(self) -> None:
        if self._video_player.is_playing():
            self.pause()
        else:
            self.play()

    def start_video(self, url: str) -> None:
        """
        Starts a new video in the VLC player.

        A new media instance is created and set. Then, the audio is muted,
        which is needed because not all the youtube-dl urls are silent.
        Finally the fullscreen is set if it was indicated as an argument.
        """

        self._logger.info("Starting new video")
        media = self._instance.media_new(url)
        self._video_player.set_media(media)
        self._video_player.audio_set_mute(True)
        self._video_player.set_fullscreen(self._fullscreen)

    def set_position(self, ms: int) -> None:
        """
        Setting the position in milliseconds
        """

        self._video_player.set_time(ms)

    # Get the position of the VLC media playing in ms
    def get_position(self) -> int:
        """
        Getting the position of the VLC player in milliseconds
        """

        return self._video_player.get_time()
