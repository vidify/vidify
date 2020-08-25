//! TODO: module-level docs

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

// TODO: add logging
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
        // TODO: maybe the trait should return `Result`? This would avoid
        // the unwraps.
        //
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
        // TODO: maybe the trait should return `Result`? This would avoid
        // the unwrap.
        self.mpv.get_property("pause").unwrap()
    }

    fn position(&self) -> u32 {
        // TODO: maybe the trait should return `Result`? This would avoid
        // the unwrap.
        // TODO: maybe the trait should return u64 or a different type?
        self.mpv.get_property::<i64>("playback_time").unwrap() as u32
    }

    fn seek(&mut self, ms: i64, relative: bool) {
        // TODO: maybe the trait should return `Result`? This would avoid
        // the unwraps.
        // TODO: should this `wait_for_property("seekable")`?
        let secs = (ms as f64 / 1000.0).round();
        if relative {
            if secs > 0.0 {
                self.mpv.seek_forward(secs).unwrap();
            } else {
                self.mpv.seek_backward(-secs).unwrap();
            }
        } else {
            self.mpv.seek_absolute(secs).unwrap();
        }
    }

    fn start_video(&mut self, media: &str, start_playing: bool) {
        // TODO: maybe the trait should return `Result`? This would avoid
        // the unwraps.
        self.mpv.command("loadfile", &[media]).unwrap();

        // Mpv starts automatically playing the video.
        if !start_playing {
            self.set_pause(false);
        }
    }
}
