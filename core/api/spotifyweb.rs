//! This implements the official web API, using the `rspotify` module.
//! The web API provides much more metadata about the Spotify player but
//! it's limited in terms of usabilty:
//!     * The user has to sign in and manually set it up
//!     * Only Spotify Premium users are able to use some functions
//!     * API calls are limited, so it's not as responsive

use crate::api::APIBase;
use crate::config::Config;
use crate::error::{Error, Result};

use std::io::{Write, BufRead, BufReader};
use std::net::{TcpListener, TcpStream};
use std::sync::mpsc;
use std::thread;
use std::time;

use log::{error, info};
use rspotify::blocking::client::Spotify;
use rspotify::blocking::oauth2::{
    SpotifyClientCredentials, SpotifyOAuth, TokenInfo,
};
use rspotify::model::playing::Playing;

pub struct SpotifyWeb {
    spotify: Spotify,
    playing: Playing,
}

impl APIBase for SpotifyWeb {
    fn new(config: &Config, sender: super::Sender) -> Result<Self> {
        let mut oauth = SpotifyOAuth::default()
            .client_id(&config.client_id.clone().ok_or(Error::SpotifyWebAuth)?)
            .client_secret(
                &config.client_secret.clone().ok_or(Error::SpotifyWebAuth)?,
            )
            .redirect_uri(&config.redirect_uri)
            .scope("user-read-currently-playing user-read-playback-state")
            .build();

        // The refresh token is attempted to be reused from previous
        // sessions.
        let token = match &config.refresh_token {
            Some(token) => oauth
                .refresh_access_token_without_cache(&token)
                .ok_or(Error::SpotifyWebAuth)?,
            // TODO: use the GUI for this once it's finished
            None => get_token(&mut oauth)?,
        };

        // Once the access token is ready, the Spotify API can be initialized.
        let creds = SpotifyClientCredentials::default()
            .token_info(token)
            .build();
        let spotify =
            Spotify::default().client_credentials_manager(creds).build();

        // A first request for the playing track will also be made in order
        // to fully initialize the internal data, and to make sure the API
        // is correctly authenticated.
        Ok(SpotifyWeb {
            playing: spotify
                .current_user_playing_track()
                .map_err(|e| Error::FailedRequest(e.to_string()))?
                .ok_or(Error::NoTrackPlaying)?,
            spotify,
        })
    }

    // fn update(&mut self) -> Result<()> {
    // self.playing = self.refresh_metadata()?;
    // }

    // fn refresh_metadata(&self) -> Result<Playing> {
    // self.spotify.current_user_playing_track()?.ok_or(Error::NoTrackPlaying)
    // }

    // There's only a single possible player name.
    fn player_name(&self) -> String {
        String::from("Spotify Web Player")
    }

    fn artist(&self) -> Option<String> {
        if let Some(item) = &self.playing.item {
            if let Some(artist) = item.artists.get(0) {
                return Some(artist.name.clone());
            }
        }

        None
    }

    fn title(&self) -> Option<String> {
        Some(self.playing.item.as_ref()?.name.clone())
    }

    fn position(&self) -> Option<time::Duration> {
        Some(time::Duration::from_millis(self.playing.progress_ms? as u64))
    }

    fn is_playing(&self) -> bool {
        self.playing.is_playing
    }

    fn event_loop(&mut self) {
        unimplemented!();
    }
}


/// A small server will be ran to obtain the access token without user
/// interaction, besides logging in to Spotify in the browser.
fn get_token(oauth: &mut SpotifyOAuth) -> Result<TokenInfo> {
    info!("Obtaining access token with web server");
    let (sx, rx) = mpsc::channel();
    let uri = oauth.redirect_uri.clone();
    thread::spawn(move || {
        let uri = to_bind_format(&uri);
        let listener = TcpListener::bind(uri).unwrap();
        for stream in listener.incoming() {
            match stream {
                Ok(stream) => match get_code(stream) {
                    Ok(code) => {
                        // Once the code is obtained successfully, it's
                        // sent to the main function, and the connection is
                        // closed.
                        info!("Obtained code: {}", code);
                        sx.send(code).unwrap();
                        break;
                    }
                    Err(e) => error!("Error when obtaining the code: {}", e)
                },
                Err(e) => error!("Unable to connect: {}", e)
            }
        }
    });

    // The authorization URL will start a new connection with the web server
    // once it's opened by the user.
    let url = oauth.get_authorize_url(None, Some(true));
    // TODO: shouldn't unwrap.
    webbrowser::open(&url).unwrap();
    let code: String = rx.recv().unwrap();
    let token = oauth
        .get_access_token_without_cache(&code)
        .ok_or(Error::SpotifyWebAuth)?;

    Ok(token)
}

/// Converting a redirect uri like `http://localhost:8888/callback/` into
/// `localhost:8888` so that it can be used for the TCP listener.
fn to_bind_format(bind_uri: &str) -> &str {
    bind_uri.split("/").nth(2).expect(
        "Invalid redirect uri, it must follow the regular expression \
                `.*//(.+:\\d+).*`.",
    )
}

fn get_code(mut stream: TcpStream) -> Result<String> {
    // Reading the request for the redirect URI. The first line of the HTTP
    // response should contain the GET data with the code.
    let mut data = BufReader::new(stream.try_clone().unwrap());
    let mut req_data = String::new();
    data.read_line(&mut req_data)?;
    info!("Request data into String: {}", req_data);

    // Indicating the user that the authentication was completed successfully.
    write!(
        &mut stream,
        "HTTP/1.1 200 OK\nContent-Type: text/html; charset=UTF-8\n\n{}",
        include_str!("spotifyweb_response.html")
    )?;

    Ok(extract_code(&req_data)?)
}

/// Obtaining the code from the HTTP request format without the need for a
/// regular expression nor a more advanced HTTP library:
///
/// ```
/// GET /callback/?code=AQBM...XGN&state=sXAJJhszLFKzcPDf HTTP/1.1
/// ```
///
/// In the previous example, the extracted code will be "AQBM...XGN".
fn extract_code(data: &str) -> Result<String> {
    let code = data.split("?code=") // Starting prefix
        .nth(1)
        .ok_or(Error::SpotifyWebAuth)?
        .split_whitespace() // May include a space before `HTTP/X.X`
        .next()
        .ok_or(Error::SpotifyWebAuth)?
        .split("&") // May include `&state=4V8JSmSUqWyn9ah8`
        .next()
        .ok_or(Error::SpotifyWebAuth)?;

    Ok(String::from(code))
}

#[cfg(test)]
mod test {
    use super::*;

    #[test]
    fn correct_bind_format() {
        assert_eq!(to_bind_format("http://localhost:0000"), "localhost:0000",);
        assert_eq!(to_bind_format("https://localhost:1234"), "localhost:1234",);
        assert_eq!(
            to_bind_format("http://localhost:8888/callback/"),
            "localhost:8888",
        );
        assert_eq!(
            to_bind_format("http://localhost:0/callback/"),
            "localhost:0",
        );
    }

    #[test]
    #[should_panic]
    fn incorrect_bind_format() {
        to_bind_format("localhost:8888");
    }
}
