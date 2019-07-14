#!/bin/bash
OUTTMPL="downloads/%(id)s.%(ext)s"
song_info="Foals - What Went Down"

youtube-dl "ytsearch:$song_info" -o "$OUTTMPL"
vlc "$filename"

