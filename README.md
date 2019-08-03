# Spotify Music Videos

A simple tool to show Youtube **music videos** and **lyrics** for the currently playing Spotify songs with VLC.

![example](screenshots/screenshot.png)

## How to install

You can use pip to install it easily:

`pip3 install spotify-videos`

Or download the latest [release](https://github.com/marioortizmanero/spotify-music-videos/releases). Uncompress the .tar.gz file and run inside the folder:

`python ./setup.py install`

*Note: you can add the --user flag to install it locally.*


## Compatibility

For Windows and Mac users, the Spotify Web API will be used. This means that:

* You have to sign in and set it up manually
* Only Spotify Premium users are able to use some functions
* API calls are limited to 1 per second so there is more lag

**How to obtain your client ID and your client secret:**

1. Go to the [Spotify Developers Dashboard](https://developer.spotify.com/dashboard/applications)
2. Create a new client ID. You can fill the descriptions as you like.
3. Click `No` when asked if it's a commercial integration and accept the terms in the next step.
4. Go to `Edit Settings` and type `http://localhost:8888/callback/` in the Redirect URIs field.
5. You can now copy your Client ID and Client Secret and add them when you call `spotify-videos`:
    * `spotify-videos --username your_username --client-id your_client_id --client-secret your_client_secret`

You may be prompted to paste the resulting link that was opened in your browser into the program. After doing it, the authorization process will be complete. The auth info should be kept in a cache file named `.cache-[your_username]`


## How to use

You can use these flags to modify the behavior of the program:

```
usage: spotify-videos [-h] [-v] [--debug] [-n] [-f] [-a VLC_ARGS]
                          [--width MAX_WIDTH] [--height MAX_HEIGHT] [-w]
                          [--username USERNAME] [--client-id CLIENT_ID]
                          [--client-secret CLIENT_SECRET]
                          [--redirect-uri REDIRECT_URI]

Windows and Mac users must pass --username, --client-id and --client-secret to
use the web API. Read more about how to obtain them in the README
(https://github.com/marioortizmanero/spotify-music-videos).

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit.
  --debug               display debug messages
  -n, --no-lyrics       do not print lyrics
  -f, --fullscreen      play videos in fullscreen mode
  -a VLC_ARGS, --args VLC_ARGS
                        other arguments used when opening VLC. Note that some
                        like args='--fullscreen' won't work in here
  --width MAX_WIDTH     set the maximum width for the played videos
  --height MAX_HEIGHT   set the maximum height for the played videos
  -w, --use-web-api     forcefully use Spotify's web API
  --username USERNAME   your Spotify username. Mandatory if the web API is
                        being used. Example: --username='yourname'
  --client-id CLIENT_ID
                        your client ID. Mandatory if the web API is being
                        used. Check the README to see how to obtain yours.
                        Example: --client-
                        id='5fe01282e44241328a84e7c5cc169165'
  --client-secret CLIENT_SECRET
                        your client secret ID. Mandatory if the web API is
                        being used. Check the README to see how to obtain
                        yours. Example: --client-
                        secret='2665f6d143be47c1bc9ff284e9dfb350'
  --redirect-uri REDIRECT_URI
                        the redirect URI for the web API. Not necessary as it
                        defaults to 'http://localhost:8888/callback/'
```

---

## Current limitations:
* Spotify doesn't currently (15/07/19) support the MPRIS property `Position` so the starting offset is calculated manually and may be a bit rough.
* To configure the maximum size of VLC's window a GUI would need to be implemented, like tkinter. The project would be much less minimal that way, but more features could be implemented, like lyrics inside the GUI.
* Spotify's Web API doesn't allow function calls on updates like Dbus, meaning that the metadata has to be manually updated every second and checked in case of changes.


## Documentation

Helpful documentation links for contributing:
* [DBus](https://dbus.freedesktop.org/doc/dbus-specification.html), [DBus python module](https://dbus.freedesktop.org/doc/dbus-python/tutorial.html)
* [MPRIS](https://specifications.freedesktop.org/mpris-spec/latest/Player_Interface.html#Property:Position)
* [python-vlc](https://www.olivieraubert.net/vlc/python-ctypes/doc/)

