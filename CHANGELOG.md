* #9: Now using a newer Spotipy fork made by Felix Hildén
* #10: Support for local Spotify info on Windows and macOS without having to use the web API.
* #11, #16: Support for mpv has been added. It can be enabled from the config file or passing --use-mpv as an argument1
* #12: A config file has been implemented
* #13: Improved documentation overall
* #14: Modules have been reorganized inside different directories

TODO:
* Add optional dependency to PKGBUILD for python-mpv
* Improve documentation for the new additions
* Automatically refresh Spotify token (save expiration date, generate a spotipy.Token instead of a string inside the web API to store it)
* Do more tests, stabilize before release
* Finish testing windows and darwin support
