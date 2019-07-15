import vlc

# VLC Instance
Instance = vlc.Instance(
        "--quiet " + # Don't print warnings to stdout
        "--no-qt-error-dialogs" # Don't print errors to stdout
)
player = Instance.media_player_new()

# playing the video on VLC
def play_video(filename):
    # Media instance
    Media = Instance.media_new(filename)
    Media.get_mrl()
    # Player instance
    player.set_media(Media)
    player.play()

