import youtube_dl

# youtube-dl configuration
ydl_opts = {
    'format' : '136/135/134/133',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'quiet' : 'true'
}
ydl = youtube_dl.YoutubeDL(ydl_opts)

def download_video(name):
    # Download the video, getting the filename
    info = ydl.extract_info("ytsearch:" + name, download=True)
    # Fix for error with prepare_filename inside youtube_dl
    return "downloads/" + info['entries'][0]['id'] + ".mp4"


