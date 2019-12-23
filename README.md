<div align="center">

<img src="images/logo.png" height=100 alt="logo" align="center"/>
<h1>Spotivids</h1>
<span>Watch <b>music videos</b> and <b>lyrics</b> for the songs playing on your computer</span>

<img alt="Travis" src="https://travis-ci.com/marioortizmanero/spotivids.svg?branch=master"> <img alt="PyPi version" src="https://img.shields.io/pypi/v/spotivids"> <img alt="AUR version" src="https://img.shields.io/aur/version/spotivids">

<hr>

<img src="images/screenshot.png" alt="Example" align="center">

</div>


## Table of contents
* [Requirements](#requirements)
* [Installation](#installation)
    * [The APIs](#the-apis)
    * [The Players](#the-players)
* [Usage and configuration](#usage)
* [FAQ](#faq)
* [Development resources](#development)
    * [Tests](#tests)
    * [Current Limitations](#current-limitations)


## Requirements
* Python 3.7+
* Other dependencies dependending on what [API](#the-apis) and [player](#the-players) you're going to use.

## Installation
* The regular installation with pip: `pip install --user vidify`. Other APIs and Players can be used by installing the extra required packages, like `pip install --user vidify[extra1, extra2]`. Read the [APIs section](#the-apis) and the [Players section](#the-players) for more. By default, Vidify includes the Spotify APIs and VLC as the player.
* You can download the latest stable [release](https://github.com/marioortizmanero/spotivids/releases). There should be binaries avaliable for Mac OS, Linux and Windows. These already include mpv support and most of the supported APIs.
* Linux:
    * Arch Linux: you can install it from the AUR: [`spotivids`](https://aur.archlinux.org/packages/spotivids/). Read the optional dependencies to use more APIs and players. Maintained by me ([marioortizmanero](https://github.com/marioortizmanero)).
    * Gentoo: there's an e-build maintained by [AndrewAmmerlaan](https://github.com/AndrewAmmerlaan) at [dev-python/spotify-music-videos](https://packages.gentoo.org/packages/dev-python/spotify-music-videos).
    * Feel free to upload it to your distro's repositories! Let me know in an issue so that I can add it to this list.


### The APIs
An API is simply a source of information about the music playing on a device. For example, the Spotify desktop client, or iTunes. This app is built to support any API as easily as possible, because there are many different ways to play music. Here are the currently supported ones:

| Name                                         | Wiki link | PyPi install | Description |
|----------------------------------------------|:---------:|--------------|-------------|
| Linux Media Players (`mpris_linux`)          | [🔗](https://github.com/marioortizmanero/spotify-music-videos/wiki/Linux-Media-Players) | Default (see wiki) | Any MPRIS compatible media player for Linux or BSD (99% of the media players). |
| Spotify for Windows & MacOS (`swspotify`)    | [🔗](https://github.com/marioortizmanero/spotify-music-videos/wiki/Spotify-for-Windows-and-MacOS) | Default | The Spotify desktop app for Windows & MacOS, using the [SwSpotify](https://github.com/SwagLyrics/SwSpotify) library. |
| Spotify Web (`spotify_web`)                  | [🔗](https://github.com/marioortizmanero/spotify-music-videos/wiki/Spotify-Web-API) | Default | The official Spotify Web API. Check the wiki for more details. |
| Unknown (any other string)                   | - | - | If you use any other string with `--api`, the initial screen to choose an API will appear. This is temporary until the GUI menu is implemented. |

The internal name inside parenthesis is used for the [arguments](#usage) and the [config](#the-config-file) options. `--api mpris_linux` would enable the Linux Media Players API, for instance.

### The players
The embedded video players inside the app. External players are used because they have better support and already come with codecs installed. The default one is VLC because it's more popular, but you can use others if you have the player installed, and the PyPi extra dependencies. For example, to install Vidify with Mpv support, you'd run `pip install --user vidify[mpv]`.

| Name           | PyPi install | Description                                           | Arguments/config options                      |
|----------------|--------------|-------------------------------------------------------|-----------------------------------------------|
| VLC (`vlc`)    | Default      | The default video player. Widely used and very solid. |`--vlc-args <VLC_ARGS>`                        |
| Mpv (`mpv`)    | `mpv`        | A simple and portable video player.                   | `--mpv-flags <MPV_ARGS>` (only boolean flags) |

For now, the only way to specify what player to use is with [arguments](#usage) or inside the [config file](#the-config-file) with the internal name between parenthesis. Use `--player mpv` or save it in your config file for future usage:

```ini
[Defaults]
player = mpv
```

## Usage
The app has an interface that will guide you through the set-up, but you can use command line arguments and the config file for more advanced options (and until the GUI is completely finished).

```
usage: spotivids [-h] [-v] [--debug] [--config-file CONFIG_PATH] [-n] [-f]
                 [--stay-on-top] [-p PLAYER] [--width WIDTH] [--height HEIGHT] [-a API]
                 [--client-id CLIENT_ID] [--client-secret CLIENT_SECRET]
                 [--redirect-uri REDIRECT_URI] [--vlc-args VLC_ARGS]
                 [--mpv-flags MPV_FLAGS]
```

| Argument                         | Description         |
|----------------------------------|---------------------|
| `-n`, `--no-lyrics`              | do not print lyrics. |
| `-f`, `--fullscreen`             | play videos in fullscreen mode. |
| `--stay-on-top`                  | the app window will stay on top of other apps. |
| `--width <WIDTH>`                | set the width for the downloaded videos (this is useful to play lower quality videos if your connection isn't good). |
| `--height <HEIGHT>`              | set the height for the downloaded videos. |
| `-a, --api`                      | specify the API to use. See the [APIs section](#the-apis) for more info about the supported APIs. |
| `-p`, `--player`                 | specify the player to use. See the [Players section](#the-players) for more info about the supported players. |
| `--config-file <PATH>`           | indicate the path of your [config file](#the-config-file).  |

### The config file
The configuration file is created by default at your usual config directory:

* Linux: `~/.config/spotivids/config.ini` (or in `$XDG_CONFIG_HOME`, if defined)
* Mac OS X: `~/Library/Preferences/spotivids/config.ini`
* Windows: `C:\Users\<username>\AppData\Local\spotivids\config.ini`

You can use a custom one by passing `--config-file <PATH>` as an argument. The config file is overriden by the configuration passed as arguments, but keeps your settings for future usage. [Here's an example of one](https://github.com/marioortizmanero/spotivids/blob/master/example.ini). It uses the [INI config file formatting](https://en.wikipedia.org/wiki/INI_file). Most options are inside the `[Defaults]` section.

All the available options for the config file are the same as the arguments listed in the [Usage section](#usage), except for `--config-file <PATH>`, which is only an argument. Their names are the same but with underscores instead of dashes. For example, `--use-mpv` would be equivalent to `use_mpv = true`.

## FAQ

### Spotivids doesn't work correctly with Python 3.8
Qt started supporting Python 3.8 with the 5.14 release. Make sure you're using an updated version and try again. `TypeError: 'Shiboken.ObjectType' object is not iterable` will be raised otherwise.

### `ModuleNotFoundError: No module named 'gi'` when using a virtual environment
For some reason, `python-gobject` may not be available inside a virtual environment. You can create a symlink inside it with:

```bash
ln -s "/usr/lib/python3.8/site-packages/gi" "$venv_dir/lib/python3.8/site-packages"
```

or install `gobject-introspection` (or the equivalent package name) and then run `pip install pygobject` to install it with pip inside the virtual environment.

---

## Development
Helpful documentation links for contributing:
* [DBus](https://dbus.freedesktop.org/doc/dbus-specification.html), [pydbus](https://github.com/LEW21/pydbus), [MPRIS](https://specifications.freedesktop.org/mpris-spec/latest/Player_Interface.html#Property:Position), [Qt for Python](https://wiki.qt.io/Qt_for_Python).
* [python-vlc](https://www.olivieraubert.net/vlc/python-ctypes/doc/), [python-mpv](https://github.com/jaseg/python-mpv).

The app logo was created by [xypnox](https://github.com/xypnox) in this [issue](https://github.com/marioortizmanero/spotivids/issues/26).

The changelog and more information about this program's versions can be found in the [Releases page](https://github.com/marioortizmanero/spotivids/releases).

Inside `dev/` you can find more information about building: [BUILDING.md](https://github.com/marioortizmanero/spotify-music-videos/blob/master/dev/BUILDING.md).

### Tests
You can run the module locally with `python -m spotivids`.

This project uses `unittest` for testing. Run them with `python -m unittest` or `python -m unittest discover -s tests`
