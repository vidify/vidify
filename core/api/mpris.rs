use crate::api::{APIBase, APIEvent};
use crate::config::Config;
use crate::error::{Result, Error};

use std::thread;
use std::time;

use mpris::{PlayerFinder, Event};
use log::{info, error};

impl From<mpris::DBusError> for Error {
    fn from(err: mpris::DBusError) -> Self {
        Error::FailedConnection(err.to_string())
    }
}

impl From<mpris::FindingError> for Error {
    fn from(err: mpris::FindingError) -> Self {
        Error::FailedConnection(err.to_string())
    }
}

pub struct MPRIS {
    title: Option<String>,
    artist: Option<String>,
    position: Option<time::Duration>,
    is_playing: bool,
}

// TODO: check `player.can_play` and similars?
impl APIBase for MPRIS {
    fn new(config: &Config, sender: super::Sender) -> Result<Self> {
        // A daemon thread will update the properties in the background.
        thread::spawn(move || {
            // TODO: remove unwraps?
            let player = PlayerFinder::new().unwrap().find_active().unwrap();
            for event in player.events().unwrap() {
                match event {
                    Ok(event) => {
                        use Event::*;
                        match event {
                            Paused => sender.send(APIEvent::Paused).unwrap(),
                            Playing => sender.send(APIEvent::Playing).unwrap(),
                            Stopped => sender.send(APIEvent::Stopped).unwrap(),
                            // Seeked{position_in_us: us} => {},
                            TrackChanged(track) => {},
                            ev => info!("Unrelated event received: {:?}", ev),
                        }
                    }
                    Err(e) => error!("DBus event error: {}", e)
                }
            }

            info!("Done reading events");
        });

        Ok(MPRIS {
            artist: None,
            title: None,
            position: None,
            is_playing: false,
        })
    }

    fn player_name(&self) -> String {
        String::from("asd")
        // self.player.lock().unwrap().bus_name().to_string()
    }

    fn artist(&self) -> Option<String> {
        None
        // self.player
        //     .lock()
        //     .unwrap()
        //     .get_metadata()
        //     .ok()?
        //     .album_artists()?
        //     .clone()
        //     .into_iter()
        //     .next()
    }

    fn title(&self) -> Option<String> {
        None
        // Some(
        //     self.player
        //         .lock()
        //         .unwrap()
        //         .get_metadata()
        //         .ok()?
        //         .title()?
        //         .to_string()
        // )
    }

    // TODO: return std::time::Duration, u128 or a more appropiate data type
    // to avoid `as`.
    fn position(&self) -> Option<time::Duration> {
        None
        // self.player.lock().unwrap().get_position().ok()
    }

    fn is_playing(&self) -> bool {
        false
        // self.player.lock().unwrap().is_running()
    }

    fn event_loop(&mut self) {
        unimplemented!();
    }
}
