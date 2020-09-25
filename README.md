<div align="center">

<img src="images/logo.png" height=100 alt="logo" align="center"/>
<h1>Vidify</h1>
<span>Watch <b>music videos in real-time</b> for the songs playing on your device</span>

<a href="https://github.com/vidify/vidify/actions"><img alt="Build Status" src="https://github.com/vidify/vidify/workflows/Continuous%20Integration/badge.svg"></a> <a href="https://pypi.org/project/vidify/"><img alt="PyPi version" src="https://img.shields.io/pypi/v/vidify"></a> <a href="https://aur.archlinux.org/packages/vidify/"><img alt="AUR version" src="https://img.shields.io/aur/version/vidify"></a> <a href="https://discord.gg/yfJSyPv"><img alt="Discord server" src="https://img.shields.io/discord/758954483802963978"></a>

<img src="images/screenshot.png" alt="Example" align="center">

</div>

*A lighter and less dev-oriented version of this README can be found at [vidify.org](https://vidify.org). The official site also has translations available.*

## Table of contents
* [Installation](#installation)
    * [The APIs](#the-apis)
    * [The Players](#the-players)
        * [The External Player](#the-external-player)
    * [Audio Synchronization](#audio-synchronization)
* [Usage and configuration](#usage)
* [FAQ](#faq)
* [Development resources](#development)
    * [Tests](#tests)
    * [Current Limitations](#current-limitations)


## Installation
Vidify ships with the most popular [music players](#the-apis) for your operating system. The music videos can be played on either [the same computer, or on a different device](#the-players).

Here are the different ways to install Vidify, depending on your Operating System:

* **Cross-platform:** With [pip](https://pypi.org/project/vidify): `pip install --user vidify`. Optional APIs and Players can be installed with `pip install --user vidify[extra1,extra2]`, which is equivalent to installing the list of dependencies needed for `extra1` and `extra2`.
* **Windows or Linux:** Using the binaries from the [latest stable releases](https://github.com/vidify/vidify/releases). These include support for all optional APIs, and use mpv as the player.
* **Linux:**
    * Arch Linux: you can install it from the AUR: [`vidify`](https://aur.archlinux.org/packages/vidify/). Maintained by me ([marioortizmanero](https://github.com/marioortizmanero)).
    * Gentoo Linux: there's an ebuild maintained by [AndrewAmmerlaan](https://github.com/AndrewAmmerlaan) in the [GURU overlay](https://wiki.gentoo.org/wiki/Project:GURU) at [media-video/vidify](https://gpo.zugaina.org/media-video/vidify): `eselect repository enable guru && emerge --sync guru && emerge vidify`
    * *Feel free to upload it to your distro's repositories! Let me know in an issue so that I can add it to this list.*

*Note: Vidify requires Python >= 3.6.*

### The APIs
An API is simply a source of information about the music playing on a device. For example, the Spotify desktop client, or iTunes. Here are the currently supported ones:

| Name                                         | Wiki link                                                                 | Extra requirements              | Description |
|----------------------------------------------|:-------------------------------------------------------------------------:|---------------------------------------|-------------|
| Linux Media Players (`mpris_linux`\*)        | [🔗](https://vidify.org/wiki/linux-media-players/)           | *Installed by default* (see the wiki) | Any MPRIS compatible media player for Linux or BSD (99% of them, like Spotify, Clementine, VLC...). |
| Spotify for Windows & MacOS (`swspotify`\*)  | [🔗](https://vidify.org/wiki/spotify-for-windows-and-macos/) | *Installed by default*                | The Spotify desktop app for Windows & MacOS, using the [SwSpotify](https://github.com/SwagLyrics/SwSpotify) library. |
| Spotify Web (`spotify_web`\*)                | [🔗](https://vidify.org/wiki/spotify-web-api/)               | *Installed by default*                | The official Spotify Web API, using [Tekore](https://github.com/felix-hilden/tekore). Check the wiki for more details on how to set it up. |

\* The name inside parenthesis is used as a key for the [arguments](#usage) and the [config](#the-config-file) options. `--api mpris_linux` would force using the Linux Media Players API, for instance. It's also used for the extra dependencies installation with pip: `pip install vidify[extra1]` would install all the extra requirements for `extra1` with pip.

### The players
The music videos can be played inside Vidify with [an embedded instance of Mpv](https://mpv.io/), or on a different device in your network with the external player.

The external player lets you play Vidify's music videos essentially anywhere. It will send all the music video information to an external application. Here are the current implementations:

* **Vidify TV**: available on Android, Android TV and Amazon Fire Stick TV. [Play Store page](https://play.google.com/store/apps/details?id=com.glowapps.vidify).

### Audio synchronization
Vidify has an audio synchronization feature. The full repository is in [vidify/audiosync](https://github.com/vidify/audiosync-rs). It's still Work-In-Progress, so it's disabled by default. It requires the following dependencies:

<!-- TODO: these will change after audiosync-rs replaces the C implementation -->
* FFTW: `libfftw3` on Debian-based distros.
* ffmpeg: `ffmpeg` on most repositories. It must be available on your path.
* pulseaudio: `pulseaudio`, pre-installed on most repos.
* youtube-dl: this is installed by default with Vidify, but make sure it's available on your path.

It can be activated with `--audiosync`, or inside your [config file](#the-config-file):

```ini
[Defaults]
audiosync = true
```

You can calibrate the audiosync results with the option `--audiosync-calibration` or `audiosync_calibration`. By default it's 0 milliseconds, but it may depend on your hardware.

*Note: if when using audiosync there's no sound on Linux, you might need to disable stream target device restore by editing the corresponing line in `/etc/pulse/default.pa` to `load-module module-stream-restore restore_device=false`.*

*Note 2: you should make sure that the sink being recorded is either `audiosync`, or the one where the music is playing. Here's an example on Pavucontrol (it's usually called 'Monitor of ...'):*

![pavucontrol](images/pavucontrol-audiosync.png)

## Usage
The app has an interface that will guide you through most of the set-up, but you can use command line arguments and the config file for more advanced options (and until the GUI is completely finished):

<div align="center">
<img src="images/screenshot_setup.png" alt="setup">
</div>


```
USAGE:
    vidify [FLAGS] [OPTIONS]

FLAGS:
        --audiosync      Enable automatic audio synchronization. Read the installation guide for more information. Note:
                         this feature is still in development
        --dark-mode      Activate the dark mode
    -d, --debug          Display debug messages
    -f, --fullscreen     Open the app in fullscreen mode
        --help           Prints help information
    -h, --height         The initial window's height
        --stay-on-top    The window will stay on top of all apps
    -V, --version        Prints version information
    -w, --width          The initial window's width

OPTIONS:
    -a, --api <api>
            The source music player used. Read the installation guide for a list with the available APIs

        --audiosync-calibration <audiosync_calibration>    Manual tweaking value for audiosync in milliseconds
        --client-id <client_id>
            The client ID for the Spotify Web API. Check the guide to learn how to obtain yours

        --client-secret <client_secret>
            The client secret for the Spotify Web API. Check the install guide to learn how to obtain yours

    -c, --conf-file <conf_file>                            The config file path
    -l, --lyrics <lyrics>                                  Choose the lyrics provider, which is "LyricWikia" by default
        --mpv-properties <mpv_properties>
            Custom properties used when opening mpv, like `msg-level=ao/sndio=no;brightness=50;sub-gray=true`.
                        See all of them here: https://mpv.io/manual/master/#options
    -p, --player <player>
            The output video player. Read the installation guide for a list with the available players

        --redirect-uri <redirect_uri>                      The redirect URI used for the Spotify Web API
```

### The config file
The configuration file is created by default at your usual config directory:

* Linux: `~/.config/vidify/config.ini` (or in `$XDG_CONFIG_HOME`, if defined)
* Mac OS X: `~/Library/Preferences/vidify/config.ini`
* Windows: `C:\Users\<username>\AppData\Local\vidify\vidify\config.ini`

You can use a custom one by passing `--config-file <PATH>` as an argument. The config file is overriden by the configuration passed as arguments, but keeps your settings for future usage. [Here's an example of one](https://github.com/vidify/vidify/blob/master/example.ini). It uses the [INI config file formatting](https://en.wikipedia.org/wiki/INI_file). Most options are inside the `[Defaults]` section.

All the available options for the config file are the same as the arguments listed in the [Usage section](#usage), except for `--config-file <PATH>`, which is only an argument. Their names are the same but with underscores instead of dashes. For example, `--use-mpv` would be equivalent to `use_mpv = true`.

## FAQ
### Vidify doesn't work correctly with Python 3.8 and PySide2
PySide2 started supporting Python 3.8 with the 5.14 release. Make sure you're using an updated version and try again. `TypeError: 'Shiboken.ObjectType' object is not iterable` will be raised otherwise.

### `ModuleNotFoundError: No module named 'gi'` when using a virtual environment
For some reason, `python-gobject` may not be available inside a virtual environment. You can create a symlink inside it with:

```bash
ln -s "/usr/lib/python3.8/site-packages/gi" "$venv_dir/lib/python3.8/site-packages"
```

or install it with pip following [this guide](https://pygobject.readthedocs.io/en/latest/getting_started.html).

### Vidify doesn't recognize some downloaded songs
If the song doesn't have a metadata field with its title and artist (the latter is optional), Vidify is unable to know what song is playing. Try to modify the metadata of your downloaded songs with VLC or any other tool.

### Not playing any videos (`HTTP Error 403: Forbidden`)
If Vidify is not playing any videos, and is throwing 403 Forbidden errors (with the `--debug` argument). The YouTube-DL cache has likely become corrupt or needs to be regenerated because of other reasons, please try deleting `~/.cache/youtube-dl`.

---

## Development
If you want to help to develop Vidify, please read the [CONTRIBUTING.md](./CONTRIBUTING.md) file.

The app logo was created by [xypnox](https://github.com/xypnox) in this [issue](https://github.com/vidify/vidify/issues/26).

The changelog and more information about this program's versions can be found in the [Releases page](https://github.com/vidify/vidify/releases).

Vidify's license is the [GPL v3](./LICENSE).
