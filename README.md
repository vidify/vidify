# Spotify Music Videos
![travis](https://travis-ci.com/marioortizmanero/spotify-music-videos.svg?branch=master) ![pypi](https://img.shields.io/pypi/v/spotify-videos) ![aur](https://img.shields.io/aur/version/spotify-videos)

A simple tool to show Youtube **music videos** and **lyrics** for the currently playing Spotify songs.

![example](images/screenshot.png)


## Table of contents
* [Requirements](#requirements)
* [Installation](#installation)
* [Usage and configuration](#usage)
    * [Advanced](#advanced)
    * [The config file](#the-config-file)
* [The web API](#the-web-api)
* [Developing resources](#developing)


## Requirements
* Python 3.6+
* VLC or mpv to play the videos

For **Linux** users:

* [PyGI](https://pygobject.readthedocs.io/en/latest/) (not packaged on PyPi, you need to install it from your distribution's repository - it's usually called python-gi, python-gobject or pygobject). Here's a quick [tutorial](https://pygobject.readthedocs.io/en/latest/getting_started.html) on how to install it on most systems.

* [GLib](https://developer.gnome.org/glib/). You most likely have it installed already.


## Installation
* You can use pip to install it: `pip3 install spotify-videos --user`. If you want to use mpv instead of VLC, just use `pip3 install 'spotify-videos[mpv]' --user` instead.

* If you're on Arch Linux, you can install it from the AUR: [`spotify-videos`](https://aur.archlinux.org/packages/spotify-videos/)

* You can also download the latest stable [release](https://github.com/marioortizmanero/spotify-music-videos/releases). Uncompress the `spotify-videos-X.Y.Z.tar.gz` file and run inside the folder: `pip3 install . --user` (or `pip3 install '.[mpv]' --user` if you want to use mpv instead of VLC)


## Usage
Just running `spotify-videos` in your terminal should work, but here's more info about how to configure this module:

```
usage: spotify-videos [-h] [-v] [--debug] [--config-file CONFIG_PATH] [-n]
                      [-f] [--use-mpv] [--width MAX_WIDTH]
                      [--height MAX_HEIGHT] [-w] [--client-id CLIENT_ID]
                      [--client-secret CLIENT_SECRET]
                      [--redirect-uri REDIRECT_URI] [--vlc-args VLC_ARGS]
                      [--mpv-flags MPV_FLAGS]
```

| Argument                         | Description         |
|----------------------------------|---------------------|
| `-n`, `--no-lyrics`              | do not print lyrics |
| `-f`, `--fullscreen`             | play videos in fullscreen mode |
| `--width <MAX_WIDTH>`            | set the maximum width for the played videos |
| `--height <MAX_HEIGHT>`          | set the maximum height for the played videos |
| `--use-mpv`                      | use [mpv](https://mpv.io/) instead of [VLC](https://www.videolan.org/vlc/index.html) to play videos. Note: requires `python-mpv`, see the [installation guide](https://github.com/marioortizmanero/spotify-music-videos) for more. |
| `-w, --use-web-api`              | use Spotify's web API. See [the web API section](#the-web-api) for more info about how to set it up. |
| `--client-id <CLIENT_ID>`        | your client ID. Mandatory if the web API is being used. Check the [web API section](#the-web-api) to learn how to obtain yours. Example: `--client-id='5fe01282e44241328a84e7c5cc169165'` |
| `--client-secret <CLIENT_SECRET>`| your client secret ID. Mandatory if the web API is being used. Check the [web API section](#the-web-api) to learn how to obtain yours. Example: `--client-secret='2665f6d143be47c1bc9ff284e9dfb350'` |


### Advanced:
| Argument                         | Description         |
|----------------------------------|---------------------|
| `--config-file <PATH>`           | indicate the path of your config file.  |
| `--vlc-args <VLC_ARGS>`          | custom arguments used when opening VLC. Note that some like `args='--fullscreen'` won't work in here |
| `--mpv-flags <MPV_ARGS>`         | custom boolean flags used when opening mpv, with dashes and separated by spaces. Not intended for customization, only debugging and simple things. If you want to load non-boolean flags and such, use a config file. |
| `--redirect-uri <REDIRECT_URI>`| optional redirect uri to get the web API authorization token. The default is http://localhost:8888/callback/ |

### The config file
The config file is created by default at your home directory with `.spotify_videos_config` as the name, but you can use a custom one by passing `--config-file <PATH>` as an argument. It's overriden by the configuration passed as arguments.

[Here's an example of one](https://github.com/marioortizmanero/spotify-music-videos/blob/master/config.ini). It uses the [INI config file formatting](https://en.wikipedia.org/wiki/INI_file) and all the options are inside the `[Defaults]` section.

All the available options for the config file are the same as the arguments above, except for `--config-file <PATH>`. Their names are always the same but with underscores instead of dashes. For example, `--use-mpv` would be equivalent to `use_mpv = True`.


## The web API
All platforms have a local way to get information from Spotify, but it may not be as reliable as the official web API, or may lack features in comparison to it, like better audio syncing or pausing the video. But it also brings other downsides, like:

* You have to sign in and set it up manually
* Only Spotify Premium users are able to use some functions
* API calls are limited to 1 per second

The web API can be enabled inside the config file or passed as arguments. Example of the section inside the config file:

```ini
use_web_api = True
client_id = 
client_secret = 
```

Or simply as arguments: `spotify-videos -w --client-id <CLIENT_ID> --client-secret <CLIENT_SECRET>`

### How to obtain your client ID and your client secret:
1. Go to the [Spotify Developers Dashboard](https://developer.spotify.com/dashboard/applications)
2. Create a new client ID. You can fill the descriptions as you like. Click `No` when asked if it's a commercial integration and accept the Terms and Conditions in the next step.
3. Go to `Edit Settings` and type `http://localhost:8888/callback/` (the default redirect uri) in the Redirect URIs field.
4. You can now copy your Client ID and Client Secret and add them when you call `spotify-videos` by saving them inside your config file or by exporting them `export SPOTIPY_CLIENT_ID='your-spotify-client-id'; export SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'`

You will be prompted to paste the resulting URL that was opened in your browser into the program. It will be a broken website but all you need is the URL. After doing it, the authorization process will be complete. The auth token will be saved into the config file for future usage.


## Developing
Helpful documentation links for contributing:
* [DBus](https://dbus.freedesktop.org/doc/dbus-specification.html), [pydbus](https://github.com/LEW21/pydbus), [MPRIS](https://specifications.freedesktop.org/mpris-spec/latest/Player_Interface.html#Property:Position)
* [python-vlc](https://www.olivieraubert.net/vlc/python-ctypes/doc/), [python-mpv](https://github.com/jaseg/python-mpv)

### Tests

You can run the module locally with `python -m spotify_videos`.

This project uses `unittest` for testing. Run them with `python -m unittest` or `python -m unittest discover -s tests`

### Current limitations

* Spotify on Linux doesn't currently support the MPRIS property `Position` so the starting offset is calculated manually and may be a bit rough.
* Spotify's Web API doesn't allow function calls on updates like DBus, meaning that the metadata has to be manually updated every second and checked in case of changes.
