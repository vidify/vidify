import vlc

# VLC Instance
Instance = vlc.Instance(
        "--play-and-exit " + # Closing after the song is finished
        "--quiet " # Don't print to stdout
)

# playing the video on VLC
def play_video(filename):
    # Media instance
    Media = Instance.media_new(filename)
    Media.get_mrl()
    # Player instance
    player = Instance.media_player_new()
    player.set_media(Media)
    player.play()

