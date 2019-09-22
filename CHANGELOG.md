* #9: Now using a newer Spotipy fork made by Felix Hildén. This brings more features and improves the web API behaviour. For example, instead of creating an annoying `.cache-username` file with API information wherever spotivideos was launched, it's saved inside the default config file.
* #10: Support for local Spotify info on Windows and macOS without having to use the web API, thanks to SwSpotify. I even contributed to the project with more features from this program.
* #11, #16: Support for mpv has been added. It can be enabled from the config file or passing --use-mpv as an argument.
* #12: A config file has been implemented. Read more about how it works inside the README.md.
* #13: Improved documentation overall.
* #14: Modules have been reorganized inside different directories.
* #15: Renamed from `spotify-videos` to `spotivids`. The previous name was confusing because it was called `spotify_videos`, `spotify-videos`, `spotify-music-videos` and `Spotify Music Videos` at the same time, and it sounded quite boring and generic. I think spotivids sounds more interesting and can be more consistent.

TODO:
* Add optional dependency to PKGBUILD for python-mpv, change description and etc
* Rename on PyPi, AUR, GitHub.
* Do more tests, stabilize before release
