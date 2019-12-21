"""
This module implements the DBus API to obtain metadata about the Spotify
player. It's based on the MediaPlayer module, which takes care of everything
else.
"""


from spotivids.api.dbus_mediaplayer import DBusMediaPlayerAPI


class SpotifyLinuxAPI(DBusMediaPlayerAPI):
    def __init__(self) -> None:
        super().__init__('org.mpris.MediaPlayer2.spotify',
                         position_feature=False)
