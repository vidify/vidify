//! TODO: module-level docs

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

pub trait PlayerBase {
    fn new(config: &Config, wid: u64) -> Result<Self>
    where
        Self: Sized;

    fn set_pause(&mut self, do_pause: bool);

    fn is_paused(&self) -> bool;

    fn position(&self) -> u32;

    /// TODO: In the future, the `relative` parameter could be turned into
    /// an enum that allows different types of seeking: relative, absolute,
    /// frames, percentage.
    fn seek(&mut self, ms: i64, relative: bool);

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
