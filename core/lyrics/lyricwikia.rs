use crate::error::Result;
use crate::lyrics::LyricsBase;

pub struct LyricWikia {}

impl LyricsBase for LyricWikia {
    fn new() -> Result<Self>
    where
        Self: Sized,
    {
        Ok(LyricWikia {})
    }

    fn get_lyrics(&self, artist: &str, title: &str) -> &str {
        "some lyrics go here"
    }
}
