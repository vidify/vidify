# Spotify Videoclips

A simple tool to show Youtube **videoclips** and **lyrics** for the currently playing Spotify songs with VLC.

![example](screenshots/screenshot.png)

## How to install

You can use pip to install it easily:

`pip3 install spotify-videoclips`

Or download the latest [release](https://github.com/marioortizmanero/spotify-videoclips/releases). Uncompress the .tar.gz file and run inside the folder:

`python ./setup.py install`

*Note: you can add the --user flag to install it locally.*
*Also, it's based on DBus so it only works on Linux.*


## How to use

You can use these flags to modify the behavior of the program:

```
usage: spotify-videoclips [-h] [-d] [-n] [-f] [-a VLC_ARGS]

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           turn on debug mode
  -n, --no-lyrics       do not display lyrics
  -f, --fullscreen      play videos in fullscreen mode
  -a VLC_ARGS, --args VLC_ARGS
                        other arguments used when opening VLC. Note that some
                        like --args='--fullscreen' won't work.
```

---

## Current limitations:
* Spotify doesn't currently (15/07/19) support the MPRIS property `Position` so the starting offset is calculated manually and may be a bit rough


## TODO

* Check native toggle pause/play with vlc API
* Argument to configure the size of the wkndow (vlc) or the quality (youtube-db)
* Check if `if _status != self.status` is necessary inside property_change
* Fullscreen args when the player is created
* Support for Web Api with spotipy: detect non-linux automatically and add args


## Documentation

Helpful documentation links for contributing:
* [DBus](https://dbus.freedesktop.org/doc/dbus-specification.html), [DBus official](https://dbus.freedesktop.org/doc/dbus-specification.html), [DBus python module](https://dbus.freedesktop.org/doc/dbus-python/tutorial.html)
* [MPRIS](https://specifications.freedesktop.org/mpris-spec/latest/Player_Interface.html#Property:Position)
* [python-vlc](https://www.olivieraubert.net/vlc/python-ctypes/doc/)

