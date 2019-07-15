# Spotify Videoclips

A simple tool to show Youtube **videoclips** and **lyrics** for the currently playing Spotify songs with VLC.

![example](screenshots/screenshot.png)

## How to install

All you have to do is to install the latest version of `youtube-dl` and `python-vlc`. With pip:

* `pip install --user youtube-dl; pip install --user python-vlc`

*Note that they're avaliable on the AUR too: [youtube-dl](https://www.archlinux.org/packages/community/any/youtube-dl/), [python-vlc](https://aur.archlinux.org/packages/python-vlc/)*.

*Also, it's based on DBus so it only works on Linux.*

---

## TODO

* Use better lyrics API/module
* Find a better cache for the videos to load them faster
* Implement offset lists with delays to start the video. That way synchronization with videoclips with different length would fit better.

## Current limitations:
* Spotify doesn't currently (15/07/19) support the MPRIS property `Position` so the starting offset is calculated manually and may be a bit rough

## Documentation

Helpful documentation links for contributing:
* [DBus](https://dbus.freedesktop.org/doc/dbus-specification.html), [DBus official](https://dbus.freedesktop.org/doc/dbus-specification.html), [DBus python module](https://dbus.freedesktop.org/doc/dbus-python/tutorial.html)
* [MPRIS](https://specifications.freedesktop.org/mpris-spec/latest/Player_Interface.html#Property:Position)
* [python-vlc](https://www.olivieraubert.net/vlc/python-ctypes/doc/)
* [youtube-dl](https://github.com/ytdl-org/youtube-dl)

