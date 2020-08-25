//! This module defines the base player trait, and lists all the
//! implementations available.

pub mod external;
pub mod mpv;

use crate::config::Config;
use crate::error::Result;

use pyo3::prelude::*;
use strum_macros::{Display, EnumString};

// #[pyenum]
#[derive(Clone, Debug, Display, EnumString)]
pub enum Player {
    Mpv,
    External,
}

/// This trait represents what a player should implement in order to control
/// its audio and video playback.
///
/// The interaction with the player shouldn't be blocking.
///
/// TODO: should all methods return `Result` instead of having "undefined
/// behaviour" when i.e. the position is obtained without a video playing?
pub trait PlayerBase {
    /// Creates a new instance of the player, given a global config structure
    /// and the window ID from the GUI where it should be shown.
    fn new(config: &Config, wid: u64) -> Result<Self>
    where
        Self: Sized;

    /// Returns the current status of the player as a boolean. `true` means
    /// the player is paused, and `false` means it's currently playing.
    ///
    /// Its behaviour is undefined if it's called before a video starts
    /// playing.
    fn is_paused(&self) -> bool;

    /// The video will be paused if `do_pause` is `true`, or will be resumed
    /// if it's `false`. If `do_pause` is already in the requested status,
    /// nothing should be done.
    ///
    /// Its behaviour is undefined if it's called before a video starts
    /// playing.
    fn set_pause(&mut self, do_pause: bool);

    /// Returns the position of the player in milliseconds.
    /// TODO: should this return a time::Duration?.
    ///
    /// Some players may not have access to the position, in which case an
    /// error will be returned.
    ///
    /// Its behaviour is undefined if it's called before a video starts
    /// playing.
    fn position(&self) -> Result<u32>;

    /// Sets the player's position in milliseconds, relative to the current
    /// position of the player. Thus, its value may be positive or negative.
    /// If the resulting position is out of bounds, it should round to the
    /// closest bound (e.g., seeking to -100 ms should seek to 0 ms instead)
    ///
    /// Its behaviour is undefined if it's called before a video starts
    /// playing.
    fn seek_relative(&mut self, ms: i64);

    /// Sets the player's position in milliseconds, starting from zero.
    /// If the resulting position is out of bounds, it should round to the
    /// closest bound (e.g., seeking to VIDEO_LEN + 100 ms should seek to
    /// VIDEO_LEN ms instead)
    ///
    /// Its behaviour is undefined if it's called before a video starts
    /// playing.
    fn seek_absolute(&mut self, ms: u32);

    /// Starts playing a new video.
    ///
    /// The video can be either an URL or a location in the user's filesystem.
    /// There shouldn't be a difference when providing these 2 types of media.
    ///
    /// `start_playing` indicates if the video is going to begin playing, or
    /// it will start paused.
    ///
    /// TODO: maybe this should follow a queue-like logic instead of by
    /// playing only one video at a time.
    fn start_video(&mut self, media: &str, start_playing: bool);
}

/// Establishes the relation between the enumeration of the available Players
/// and their implementations, instantiating the selected one.
pub fn init_player(
        player: Player,
        config: &Config,
        wid: u64,
    ) -> Result<Box<dyn PlayerBase>>
{
    let player: Box<dyn PlayerBase> = match player {
        Player::Mpv => Box::new(mpv::Mpv::new(config, wid)?),
        Player::External => Box::new(external::External::new(config, wid)?),
    };

    Ok(player)
}
