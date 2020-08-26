//! TODO: module-level docs

use crate::config::Config;
use crate::error::Result;
use crate::player::PlayerBase;

pub struct External {}

impl PlayerBase for External {
    fn new(config: &Config, wid: u64) -> Result<Self> {
        Ok(External {})
    }

    fn set_pause(&mut self, do_pause: bool) {}

    fn is_paused(&self) -> bool {
        true
    }

    fn position(&self) -> Result<u32> {
        Ok(0)
    }

    fn seek_relative(&mut self, ms: i64) {}

    fn seek_absolute(&mut self, ms: u32) {}

    fn start_video(&mut self, media: &str, start_playing: bool) {}
}
