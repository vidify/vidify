//! Mpv is used as the embedded player, which is what it's designed for.
//! It's lightweight, precise and fast, which makes it perfect for
//! synchronizing audio and video with the audiosync extension.

use crate::config::Config;
use crate::error::{Error, Result};
use crate::player::PlayerBase;

use log::info;

type MpvResult<T> = libmpv::Result<T>;

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
        // Setting the base properties before mpv is initialized.
        let mpv = libmpv::Mpv::with_initializer(|init| -> MpvResult<()> {
            init.set_property("wid", wid as i64)?;
            init.set_property("vo", "gpu,libmpv,x11")?;
            init.set_property("config", false)?;
            // The audio is always muted, which is needed because not all the
            // youtube-dl videos are silent.
            init.set_property("mute", true)?;
            // The keep-open flag stops mpv from closing after the video is
            // over.
            init.set_property("keep-open", "always")?;

            for (key, val) in config.mpv_properties.iter() {
                init.set_property(key.as_str(), val.as_str())?;
            }

            Ok(())
        })?;

        Ok(Mpv {
            mpv
        })
    }

    fn set_pause(&mut self, do_pause: bool) {
        info!("Setting pause to {}", do_pause);

        // This doesn't check if it's already paused because mpv already
        // should take care of that.
        // TODO: check that this is true.
        if do_pause {
            self.mpv.pause().unwrap();
        } else {
            self.mpv.unpause().unwrap();
        }
    }

    fn is_paused(&self) -> bool {
        self.mpv.get_property("pause").unwrap()
    }

    fn position(&self) -> Result<u32> {
        let pos = self.mpv.get_property::<i64>("playback_time")?;
        Ok(pos as u32)
    }

    fn seek_relative(&mut self, ms: i64) {
        info!("Seeking to relative {} ms", ms);

        let secs = (ms as f64 / 1000.0).round();
        // TODO: should this `wait_for_property("seekable")`?
        if secs > 0.0 {
            self.mpv.seek_forward(secs).unwrap();
        } else {
            self.mpv.seek_backward(-secs).unwrap();
        }
    }

    fn seek_absolute(&mut self, ms: u32) {
        info!("Seeking to absolute {} ms", ms);

        let secs = (ms as f64 / 1000.0).round();
        // TODO: should this `wait_for_property("seekable")`?
        self.mpv.seek_absolute(secs).unwrap();
    }

    fn start_video(&mut self, media: &str, start_playing: bool) {
        info!("Starting new media '{}', playing? {}", media, start_playing);

        self.mpv.command("loadfile", &[media]).unwrap();

        // Mpv starts automatically playing the video.
        if !start_playing {
            self.set_pause(false);
        }
    }
}
