* Closes #9: Now using a newer Spotipy fork made by Felix Hildén
* Closes #11: Support for mpv has been added. It can be enabled from the config file or passing --use-mpv as an argument1
* Closes #12: A config file has been implemented
* Closes #14: Modules have been reorganized inside different directories

TODO:
* Add optional dependency to PKGBUILD for python-mpv
* Improve documentation for the new additions
* Automatically refresh Spotify token (save expiration date, generate a spotipy.Token instead of a string inside the web API to store it)
* Do more tests, stabilize before release
* Finish testing windows and darwin support
