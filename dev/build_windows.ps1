# Requires 7z and wget installed
$MPV_URL = "https://downloads.sourceforge.net/project/mpv-player-windows/libmpv/mpv-dev-x86_64-20200405-git-c5f8ec7.7z?r=https%3A%2F%2Fsourceforge.net%2Fprojects%2Fmpv-player-windows%2Ffiles%2Flibmpv%2Fmpv-dev-x86_64-20200405-git-c5f8ec7.7z%2Fdownload&ts=1586353127"


# Temporary Vidify folder to apply patches
echo ">> Copying module..."
if ( Test-Path -Path vidify ) {
	rm -r vidify
}
cp -r ../vidify .

$version = ((Get-Content vidify/version.py) -split '"' | Select -Index 1)


echo ">> Applying pre-build patches..."

# Calling get_distribution at runtime to check if modules are installed
# doesn't work with PyInstaller, so the is_installed function is overridden:
# https://github.com/pyinstaller/pyinstaller/issues/4795
Add-Content "./vidify/__init__.py" @"
def is_installed(*args):
    for s in args:
        if s not in ('python-mpv', 'zeroconf', 'swspotify', 'tekore'):
            return False
    return True
"@


echo ">> Running PyInstaller..."
pyinstaller windows.spec --noconfirm


echo ">> Applying post-build patches..."

# Tekore needs its VERSION file, which is ignored by pyinstaller because
# it isn't a Python file.
if (!(Test-Path "./dist/vidify/tekore/VERSION" -PathType Leaf)) {
    if (!(Test-Path "./dist/vidify/tekore")) {
        New-Item -Path "./dist/vidify/tekore" -ItemType Directory
    }
    wget "https://raw.githubusercontent.com/felix-hilden/tekore/master/tekore/VERSION" -O "./dist/vidify/tekore/VERSION"
}

# Including mpv
if (!(Test-Path mpv-1.dll -PathType Leaf)) {
    wget "$MPV_URL" -O "libmpv.7z" -UserAgent "[Microsoft.PowerShell.Commands.PSUserAgent]::Chrome"
    7z e "libmpv.7z"
}
cp "mpv-1.dll" "./dist/vidify"


echo ">> Compressing..."
Compress-Archive -Path "./dist/vidify" -Force -DestinationPath "vidify-v${version}_win10_x86_64.zip"
