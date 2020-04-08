# Temporary Vidify folder to apply patches
echo "Copying module..."
if ( Test-Path -Path vidify ) {
	rm -r vidify
}
cp -r ../vidify .

$version = ( ( Get-Content vidify/version.py ) -split '"' | Select -Index 1 )

# Calling get_distribution at runtime to check if modules are installed
# doesn't work with PyInstaller, so the is_installed function is overridden:
# https://github.com/pyinstaller/pyinstaller/issues/4795
echo -e \
'def is_installed(*args):
    for s in args:
        if s not in ("python-mpv", "zeroconf", "swspotify", "tekore"):
            return False
    return True' >> vidify/__init__.py


echo "Running PyInstaller..."
pyinstaller windows.spec --noconfirm

echo "Applying post-build patches..."

# Tekore needs its VERSION file, which is ignored by pyinstaller because
# it isn't a Python file.
mkdir dist/vidify/tekore
wget "https://raw.githubusercontent.com/felix-hilden/tekore/master/tekore/VERSION" -O "dist/vidify/tekore/VERSION"

echo "Compressing..."
Compress-Archive -Path dist/vidify -DestinationPath "vidify-${version}_win10_x86_64.zip"
