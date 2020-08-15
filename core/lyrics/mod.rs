//! Defines the lyrics providers the basic functionalities they must provide,
//! while listing the available implementations.

mod lyricwikia;

use crate::error::Result;
use crate::lyrics::lyricwikia::LyricWikia;

use pyo3::prelude::*;
use strum_macros::{Display, EnumString};

// #[pyenum]
#[derive(Clone, Debug, Display, EnumString)]
pub enum Lyrics {
    None,
    LyricWikia,
}

impl Default for Lyrics {
    fn default() -> Self {
        Lyrics::LyricWikia
    }
}

pub trait LyricsBase {
    fn new() -> Result<Self>
    where
        Self: Sized;

    fn get_lyrics(&self, artist: &str, title: &str) -> &str;
}

pub fn init_lyrics(lyrics: Lyrics) -> Result<Option<Box<dyn LyricsBase>>> {
    let lyrics: Option<Box<dyn LyricsBase>> = match lyrics {
        Lyrics::None => None,
        Lyrics::LyricWikia => Some(Box::new(LyricWikia::new()?)),
    };

    Ok(lyrics)
}
