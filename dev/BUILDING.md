# Building.md

Building is only done on Windows for now, because for Linux it's available on the distro repositories and it's easier to install. It uses PyInstaller and has trouble with a couple files that aren't automatically installed. For now, these are the steps to follow when building:

1. `pyinstaller windows.spec --noconfirm`.
2. Go to `dist/vidify`.
3. Create a `tekore` folder and inside it, save this: `https://raw.githubusercontent.com/felix-hilden/tekore/master/tekore/VERSION`.
4. Copy the `vidify` python folder and only leave `vidify/gui/res/` there to include the icons, fonts...
