<div align="center">

<img src="images/logo.png" height=100 alt="logo" align="center"/>
<h1>Vidify</h1>
<span>Kijk <b>muziek video's in real-time</b> voor muziek die afspeelt op jouw apparaat</span>

<a href="https://github.com/vidify/vidify/actions"><img alt="Build Status" src="https://github.com/vidify/vidify/workflows/Continuous%20Integration/badge.svg"></a> <a href="https://pypi.org/project/vidify/"><img alt="PyPi version" src="https://img.shields.io/pypi/v/vidify"></a> <a href="https://aur.archlinux.org/packages/vidify/"><img alt="AUR version" src="https://img.shields.io/aur/version/vidify"></a>

<img src="images/screenshot.png" alt="Example" align="center">

</div>

READMEs: [🇬🇧](README.md) [🇳🇱](README-nl_NL.md)

## Table of contents
* [Installatie](#installation)
    * [De APIs](#the-apis)
    * [De Videospelers](#the-players)
        * [De Externe speler](#the-external-player)
    * [Audio Synchronisatie](#audio-synchronization)
* [Gebruik en Configuratie](#usage)
* [FAQ](#faq)
* [Ontwikkelaars middelen](#development)
    * [Testen](#tests)
    * [Actuele Limitaties](#current-limitations)


## Installation
Vidify is ontwikkeld om modulair te zijn. Standaard bevat deze ondersteuning voor de meeste populaire muziekspelers (zie ook [APIs](#the-apis)). Hetzelfde geld voor de [videospelers](#the-players) (standaard [VLC](https://www.videolan.org/vlc/index.html) op het moment). Functionaliteit kan worden uitgebreid door de daarvoor nodige software te installeren, deze zijn gedocumenteerd in hun respectievelijke hoofdstukken.

Hier zijn de verschillende manier om Vidify te installeren, afhankelijk van jouw besturingssysteem:

* **Cross-platform:** Met [pip](https://pypi.org/project/vidify): `pip install --user vidify`. Optionele APIs en Videospelers kunnen worden geïnstalleerd met `pip install --user vidify[extra1,extra2]`, dit is equivalent aan het installeren van de lijst van benodigdheden voor `extra1` en `extra2`.
* **Windows of Linux:** Met gebruik van de binaire [recentste stabiele versie](https://github.com/vidify/vidify/releases). Deze bevatten ondersteuning voor alle optionele APIs en Videospelers.
* **Linux:**
    * Elke distro: je kunt gebruik maken van [snap](https://snapcraft.io/vidify-qt), installeer met: `snap install vidify-qt`.
    * Arch Linux: je kunt dit vinden in de AUR: [`vidify`](https://aur.archlinux.org/packages/vidify/). Onderhouden door mijzelf ([marioortizmanero](https://github.com/marioortizmanero)).
    * Gentoo Linux: er is een ebuild onderhouden door [AndrewAmmerlaan](https://github.com/AndrewAmmerlaan) in de [GURU overlay](https://wiki.gentoo.org/wiki/Project:GURU) genaamd [media-video/vidify](https://gpo.zugaina.org/media-video/vidify): `eselect repository enable guru && emerge --sync guru && emerge vidify`
    * *Voel je vrij om dit te uploaden naar de repositories van jouw distro! Laat me dit weten in een issue zodat ik dit aan deze lijst kan toevoegen.*

*Opmerking: Vidify werkt alleen met Python >= 3.6.*

### De APIs
Een API is een bron van informatie over welke muziek er op het moment op jouw apparaat afspeelt. Zoals bijvoorbeeld: de Spotify desktop client, of iTunes. Deze APIs zijn op het moment ondersteund:

| Naam                                         | Wiki link                                                                 | Extra vereisten                         | Beschrijving |
|----------------------------------------------|:-------------------------------------------------------------------------:|-----------------------------------------|--------------|
| Linux Media Players (`mpris_linux`\*)        | [🔗](https://github.com/vidify/vidify/wiki/Linux-Media-Players)            | *Standaard geïnstalleerd* (zie de wiki) | Elke MPRIS compatibele mediaspeler voor Linux of BSD (99% zou zeker moeten werken, zoals Spotify, Clementine, VLC...). |
| Spotify voor Windows & MacOS (`swspotify`\*) | [🔗](https://github.com/vidify/vidify/wiki/Spotify-for-Windows-and-MacOS)  | *Standaard geïnstalleerd*               | De Spotify desktop app voor Windows & MacOS, maakt gebruik van de [SwSpotify](https://github.com/SwagLyrics/SwSpotify) library. |
| Spotify Web (`spotify_web`\*)                | [🔗](https://github.com/vidify/vidify/wiki/Spotify-Web-API)                | *Standaard geïnstalleerd*               | De officiële Spotify Web API, maakt gebruik van [Tekore](https://github.com/felix-hilden/tekore). Zie de wiki voor instructies over hoe je dit instelt. |

\* De naam tussen haakjes wordt gebruikt als identificatie sleutel in [argumenten](#usage) en het [config bestand](#the-config-file). `--api mpris_linux` zou bijvoorbeeld het gebruik van de Linux Media Players API forceren. Dit wordt ook gebruikt om extra vereisten te installeren met pip: `pip install vidify[extra1]` zou de extra software installeren die benodigd is voor `extra1` met pip.

### De Videospelers
De in de app ingebedde videospelers. De standaard is VLC, omdat deze het meest populair is. Maar het staat je vrij om andere te gebruiken, als je de videospeler zelf en de daarbij horende Python modules hebt geïnstalleerd.

| Naam                  | Extra vereisten                                   | Beschrijving                                                                                               | Argumenten/config opties                      |
|-----------------------|---------------------------------------------------|------------------------------------------------------------------------------------------------------------|-----------------------------------------------|
| VLC (`vlc`)           | [VLC](https://www.videolan.org/vlc/#download)     | De standaard videospeler. veel gebruikt en heel stabiel.                                                   |`--vlc-args <VLC_ARGS>`                        |
| Mpv (`mpv`)           | [Mpv](https://mpv.io/installation/), `python-mpv` | Een opdrachtregel portable videospeler. Lichter en preciezer dan VLC.                                      | `--mpv-flags <MPV_ARGS>` (alleen booleans) |
| External (`external`) | Standaard geïnstalleerd                           | Speel de video's af op een extern apparaat. Zie het hoofdstuk over [externe speler selectie](#the-external-player) voor meer inforamtie.  | Geen                                          |

Op het moment is de enige manier om te specificeren welke videospeler er gebruikt wordt met [argumenten](#usage) of in het [config bestand](#the-config-file) met de interne naam. Bijvoorbeeld `--player mpv` of dit maar dan opgeslagen in het config bestand:

```ini
[Defaults]
player = mpv
```

#### De Externe speler
De externe speler laat jou Vidify's muziekvideo's praktisch overal afspelen. Het stuurt alle informatie over de muziekvideo naar een externe applicatie. Hier zijn de huidige implementaties:

* **Vidify TV**: beschikbaar voor Android, Android TV en Amazon Fire Stick TV. [Play Store page](https://play.google.com/store/apps/details?id=com.glowapps.vidify).

### Audio Synchronisatie
Vidify heeft een audio synchronisatie functie. Deze is hier beschikbaar: [vidify/audiosync](https://github.com/vidify/audiosync). Het is nog niet volledig functioneel.

Voorlopig is Audiosync alleen beschikbaar voor Linux. Het wordt sterk aangeraden om hierbij Mpv als videospeler te gebruiken. Je kan dit installeren met `pip install vidify[audiosync]`, samen met de volgende extra vereisten:

* FFTW: `libfftw3` op Debian gebaseerde distros.
* ffmpeg: `ffmpeg` beschikbaar voor praktisch alle distros. Moet beschikbaar zijn in jouw path.
* pulseaudio: `pulseaudio`, bijna altijd al geïnstalleerd.
* youtube-dl: dit wordt al geïnstalleerd door Vidify, maar zorg ervoor dat dit beschikbaar is in jouw path.

Het is ook beschikbaar als [`vidify-audiosync`](https://aur.archlinux.org/packages/vidify-audiosync) in de AUR en als [media-video/vidify-audiosync](https://gpo.zugaina.org/media-video/vidify-audiosync) in de [GURU overlay](https://wiki.gentoo.org/wiki/Project:GURU).

Deze functie wordt geactiveerd met het `--audiosync` argument, of in het config bestand [config file](#the-config-file):

```ini
[Defaults]
audiosync = true
```

Je kunt de resultaten van audiosync kalibreren met de optie `--audiosync-calibration` of `audiosync_calibration`. Standaard is deze 0 milliseconden, maar dit is mogelijk afhankelijk van jouw hardware.

*Opmerking: als er geen geluid is, dan moet je misschien 'stream target device restore' uitzetten door de corresponderende lijn in `/etc/pulse/default.pa` te veranderen naar `load-module module-stream-restore restore_device=false`.*

*Opmerking 2: bevestig dat de sink waarvan wordt opgenomen `audiosync` is, of de sink waar de muziek op afspeelt. Hier is een voorbeeld in Pavucontrol (Meestal heet dit 'Monitor of ...'):*

![pavucontrol](images/pavucontrol-audiosync.png)

## Gebruik
Deze app heeft een interface die je door het grootste gedeelte van de set-up begeleid, maar kunt ook opdrachtlijn argumenten en het config bestand gebruiken voor meer geavanceerde opties (totdat de GUI helemaal af is):

<div align="center">
<img src="images/screenshot_setup.png" alt="setup">
</div>


```
usage: vidify [-h] [-v] [--debug] [--config-file CONFIG_FILE] [-n] [-f] [--dark-mode] [--stay-on-top]
              [--width WIDTH] [--height HEIGHT] [-a API] [-p PLAYER] [--audiosync]
              [--audiosync-calibration AUDIOSYNC_CALIBRATION] [--vlc-args VLC_ARGS]
              [--mpv-flags MPV_FLAGS] [--client-id CLIENT_ID] [--client-secret CLIENT_SECRET]
              [--redirect-uri REDIRECT_URI]
```

| Argument                         | Beschrijving        |
|----------------------------------|---------------------|
| `-n`, `--no-lyrics`              | print de songtekst niet. |
| `-f`, `--fullscreen`             | speel af in volledig scherm modus. |
| `--dark-mode`                    | zet de GUI in dark-mode. |
| `--stay-on-top`                  | de app blijft boven alle andere apss. |
| `--width <WIDTH>`                | stel de breedte in van de gedownloade video's (dit is handig om video's met eeen lagere kwaliteit af te spelen voor als je internet traag is). |
| `--height <HEIGHT>`              | stel de hoogte van de video in. |
| `-a`, `--api`                    | specificeer de API om te gebruiken. Zie het hoofdstuk over [APIs](#the-apis) voor meer informatie over de ondersteunde APIs. |
| `-p`, `--player`                 | specificeer de videospeler om te gerbuike. Zie het hoofdstuk over [Videospelers](#the-players) voor meer informatie over de ondersteunde videospelers. |
| `--audiosync`                    | zet de [Audio Synchronisatie](#audio-synchronization) functie aan (standaard uit). |
| `--audiosync-calibration`        | kalibreer de vertraging in milliseconden die de audiosync terug stuurt. Deze kan positief of negatief zijn. Standaard is 0ms. |
| `--config-file <PATH>`           | stel het pad naar je [config bestand](#the-config-file) in.  |

### Het config bestand
Het config bestand wordt standaard gemaakt in de gebruikelijke map:

* Linux: `~/.config/vidify/config.ini` (of `$XDG_CONFIG_HOME`, als dit gedefinieerd is)
* Mac OS X: `~/Library/Preferences/vidify/config.ini`
* Windows: `C:\Users\<username>\AppData\Local\vidify\vidify\config.ini`

Je kan een andere map selecteren met het  `--config-file <PATH>` argument. Waardes in het config bestand worden overschreven door de argumenten, maar blijven wel bewaard voor de toekomst. [Hier is een voorbeeld](https://github.com/vidify/vidify/blob/master/example.ini). Het [INI config bestand formaat](https://en.wikipedia.org/wiki/INI_file) wordt gebruikt. De meest opties komen onder de kop [Defaults]`.

Alle beschikbare opties voor het config bestand zijn hetzelfde als de argumenten zoals in het hoofdstuk [Gebruik](#usage), behalve voor `--config-file <PATH>`, wat alleen een argument is. De namen zijn hetzelfde maar met een laag streepje in plaats van een normaal streepje. Bijvoorbeeld, `--use-mpv` wordt `use_mpv = true`.

## FAQ
### Vidify werkt niet goed met Python 3.8 en PySide2
PySide2 heeft pas Python 3.8 ondersteuning vanaf versie 5.14. Zorg er dus voor dat je minimaal deze versie gebruikt en probeer het nog een keer. `TypeError: 'Shiboken.ObjectType' object is not iterable` is de foutmelding die je anders zult zien.

### `ModuleNotFoundError: No module named 'gi'` when using a virtual environment
`python-gobject` is niet altijd beschikbaar in een virtuele omgeving. Om hier omheen te werken kun je een symlink maken met:

```bash
ln -s "/usr/lib/python3.8/site-packages/gi" "$venv_dir/lib/python3.8/site-packages"
```

of installeer dit met pip volgens [deze handleiding](https://pygobject.readthedocs.io/en/latest/getting_started.html).

### Vidify herkent sommige gedownloade nummers niet
Als het nummer geen metadata veld heeft met titel en artiest (waarvan artiest optioneel is), dan kan Vidify niet weten welk nummer er afspeelt. Probeer de relevante metadata aan deze gedownloade nummers toe te voegen met VLC of een ander programma.

### `FileNotFoundError: Could not find module 'libvlc.dll'.`
Zorg ervoor dat zowel Python als VLC beide 32 bits of 64 bits zijn, en dus niet verschillend. Als het goed is heb je een map genaamd `C:\Program Files (x86)\VideoLAN\VLC` (32b), of `C:\Program Files\VideoLAN\VLC` (64b).

---

## Ontwikkeling
Handige documentatie en links voor het bijdragen aan Vidify:
* [DBus](https://dbus.freedesktop.org/doc/dbus-specification.html), [pydbus](https://github.com/LEW21/pydbus), [MPRIS](https://specifications.freedesktop.org/mpris-spec/latest/Player_Interface.html#Property:Position), [Qt for Python](https://wiki.qt.io/Qt_for_Python).
* [python-vlc](https://www.olivieraubert.net/vlc/python-ctypes/doc/), [python-mpv](https://github.com/jaseg/python-mpv).

Het app logo is gemaakt door [xypnox](https://github.com/xypnox) in deze [issue](https://github.com/vidify/vidify/issues/26).

De changelog en andere informatie over de versies van dit programma vind je op de [Releases pagina](https://github.com/vidify/vidify/releases).

### Externe spelers implementatie
Het Vidify externe speler protocol is open voor iedereen om te implementeren in hun eigen applicaties om videos af te spelen. Je kunt er in dit [wiki artikel](https://github.com/vidify/vidify/wiki/%5BDEV%5D-External-Player-Protocol) meer over lezen.

### Tests
Je kunt deze applicatie lokaal uitvoeren met `python -m vidify`.

Dit project gebruikt`unittest` voor testen. Je kunt dit uitvoeren met `python -m unittest`. Je hebt wel wat extra software nodig wil dit werken.
