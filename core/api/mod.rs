pub mod macos;
pub mod mpris;
pub mod spotifyweb;
pub mod windows;

use crate::config::Config;
use crate::error::Result;

use std::time;

use pyo3::prelude::*;
use strum_macros::{Display, EnumString};

pub type Sender = std::sync::mpsc::Sender<APIEvent>;

// #[pyenum]
#[derive(Clone, Debug, Display, EnumString)]
pub enum API {
    #[cfg(any(target_os = "linux", target_os = "bsd"))]
    MPRIS,
    #[cfg(target_os = "windows")]
    Windows,
    #[cfg(target_os = "macos")]
    MacOS,
    SpotifyWeb,
}

/// The possible events that may be notified from an API.
#[derive(Clone, Debug)]
pub enum APIEvent {
    Playing,
    Paused,
    Stopped,
    Seeked(time::Duration),
    TrackChanged(String),
}

/// The abstract base class used for any API in this app. The API is defined
/// as an object that can provide information about the status of the player.
pub trait APIBase {
    /// Initializes the connection with the API, so it may block.
    ///
    /// An `Error::ConnectionFailed` exception should be raised if the attempt
    /// to connect didn't succeed. For example, if the player isn't open or
    /// if no songs are playing at that moment.
    fn new(config: &Config, sender: Sender) -> Result<Self>
    where
        Self: Sized;

    /// Returns the API's identification name for the player that's being
    /// used. For example, the Spotify Web API will always have 'Spotify',
    /// but other APIs like MPRIS can have multiple names, like 'VLC',
    /// 'Clementine'...
    fn player_name(&self) -> String;

    /// Returns the artist of the currently playing song.
    ///
    /// If it has more than one artist, the most relevant one (or just the
    /// first one) should be returned.
    fn artist(&self) -> Option<String>;

    /// Returns the title of the currently playing song.
    fn title(&self) -> Option<String>;

    /// Returns the position in milliseconds of the currently playing song.
    fn position(&self) -> Option<time::Duration>;

    /// Returns a boolean that indicates whether the song is playing at that
    /// moment or not (as in being paused).
    fn is_playing(&self) -> bool;

    /// Runs an iteration of the event loop.
    ///
    /// The event loop is a function that can be run periodically to check
    /// for updates in the API's metadata and act accordingly (start a new
    /// video, pause it, etc).
    ///
    /// This method may not be needed in some APIs, which should raise
    /// `NotImplementedError` instead. This information is saved in the API
    /// entry inside the API list so that the event loop isn't called.
    fn event_loop(&mut self);
}

/// Establishes the relation between the enumeration of the available APIs
/// and their implementations, instantiating the selected one.
pub fn init_api(
        api: API,
        config: &Config,
        sender: Sender,
    ) -> Result<Box<dyn APIBase>>
{
    let api: Box<dyn APIBase> = match api {
        #[cfg(any(target_os = "linux", target_os = "bsd"))]
        API::MPRIS => Box::new(mpris::MPRIS::new(config, sender)?),
        #[cfg(target_os = "windows")]
        API::Windows => Box::new(windows::Windows::new(config, sender)?),
        #[cfg(target_os = "macos")]
        API::MacOS => Box::new(macos::MacOS::new(config, sender)?),
        API::SpotifyWeb => Box::new(spotifyweb::SpotifyWeb::new(config, sender)?),
    };

    Ok(api)
}
