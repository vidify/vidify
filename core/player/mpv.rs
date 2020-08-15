use crate::config::Config;
use crate::error::{Error, Result};
use crate::player::PlayerBase;

impl From<libmpv::Error> for Error {
    fn from(err: libmpv::Error) -> Self {
        Error::PlayerInit(err.to_string())
    }
}

pub struct Mpv {
    mpv: libmpv::Mpv,
}

impl PlayerBase for Mpv {
    fn new(config: &Config, wid: u64) -> Result<Mpv> {
        let mpv = libmpv::Mpv::new()?;
        mpv.add_property("wid", wid as isize);

        Ok(Mpv {
            mpv
        })
    }

    fn pause(&mut self) {}

    fn is_paused(&self) -> bool {
        true
    }

    fn position(&self) -> u32 {
        123
    }

    fn seek(&mut self) {}

    fn start_video(&mut self) {}
}
