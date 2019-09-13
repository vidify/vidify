# Spotify Music Videos
![travis](https://travis-ci.com/marioortizmanero/spotify-music-videos.svg?branch=master) ![pypi](https://img.shields.io/pypi/v/spotify-videos) ![aur](https://img.shields.io/aur/version/spotify-videos)

A simple tool to show Youtube **music videos** and **lyrics** for the currently playing Spotify songs. Check the [wiki](https://github.com/marioortizmanero/spotify-music-videos/wiki) for more.

![example](images/screenshot.png)


## Requirements
* Python 3.6+
* VLC or mpv to play the videos

For **Linux** users:

* [PyGI](https://pygobject.readthedocs.io/en/latest/) (not packaged on PyPi, you need to install it from your distribution's repository - it's usually called python-gi, python-gobject or pygobject). Here's a quick [tutorial](https://pygobject.readthedocs.io/en/latest/getting_started.html) on how to install it on most systems.

* [GLib](https://developer.gnome.org/glib/). You most likely have it installed already.


## How to install
* You can use pip to install it: `pip3 install spotify-videos --user`. If you want to use mpv instead of VLC, just use `pip3 install 'spotify-videos[mpv]' --user` instead.

* If you're on Arch Linux, you can install it from the AUR: [`spotify-videos`](https://aur.archlinux.org/packages/spotify-videos/)

* You can also download the latest [release](https://github.com/marioortizmanero/spotify-music-videos/releases). Uncompress the `spotify-videos-X.Y.Z.tar.gz` file and run inside the folder: `pip3 install . --user` (or `pip3 install '.[mpv]' --user` if you want to use mpv instead of VLC)


## How to use
All usage and configuration info can be found inside [this wiki's article](https://github.com/marioortizmanero/spotify-music-videos/wiki/Configuration-and-usage).
