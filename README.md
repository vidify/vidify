# Spotify Videoclips

A simple tool to show Youtube **videoclips** and **lyrics** for the currently playing Spotify songs with VLC.

![example](screenshots/screenshot.png)

## Dependencies

* `youtube-dl`: used to download the videos since the VLC python API doesn't seem to be able to do it directly
* `python-vlc`: used to open a pop-up with the videos

## How to install

The project is currently in progress. An installation guide will be provided once it's finished. 

## TODO

* Use better lyrics API/module
* Find a better cache for the videos to load them faster
* Implement offset lists with delays to start the video. That way synchronization with videoclips with different length would fit better.
* Investigate error messages: 
```
libva error: va_getDriverName() failed with operation failed,driver_name=radeonsi
Failed to open VDPAU backend libvdpau_radeonsi.so: cannot open shared object file: No such file or directory
Failed to open VDPAU backend libvdpau_radeonsi.so: cannot open shared object file: No such file or directory
```

## Documentation

Helpful documentation links for contributing:
* [DBus](https://dbus.freedesktop.org/doc/dbus-specification.html), [DBus official](https://dbus.freedesktop.org/doc/dbus-specification.html)
* [MPRIS](https://specifications.freedesktop.org/mpris-spec/latest/Player_Interface.html#Property:Position)
* [python-vlc](https://www.olivieraubert.net/vlc/python-ctypes/doc/)
* [youtube-dl](https://github.com/ytdl-org/youtube-dl)

