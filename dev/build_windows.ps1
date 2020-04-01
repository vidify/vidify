# Temporary Vidify folder to apply patches
echo "Copying module..."
$DIR = "vidify"
if ( Test-Path -Path $DIR ) {
	rm -r $DIR
}
cp -r ../vidify .

$version = ( ( Get-Content vidify/version.py ) -split '"' | Select -Index 1 )

echo "Running PyInstaller..."
pyinstaller windows.spec --noconfirm

echo "Applying post-build patches..."

# Tekore needs its VERSION file, which is ignored by pyinstaller because
# it isn't a Python file.
mkdir dist/vidify/tekore
wget "https://raw.githubusercontent.com/felix-hilden/tekore/master/tekore/VERSION" -O "dist/vidify/tekore/VERSION"

echo "Compressing..."
Compress-Archive -Path dist/vidify -DestinationPath "vidify-${version}_win10_x86_64.zip"
