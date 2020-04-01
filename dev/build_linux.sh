#!/bin/sh

# This temporary folder will be used to modify Vidify's code automatically
# for different fixes and workarounds.
echo "Copying module..."
rm -rf vidify
cp -r  ../vidify .

version=$(awk '{print $3}' vidify/version.py | tr -d '"')

echo "Applying pre-build patches..."

# The issue with Linux building is that there can't be a directory and a file
# with the same name at once. But both the generated binary and the directory
# with all the resources are named the same (vidify). For now, temporarily
# modifying the resources directory used will do the trick.
# Assuming the global variable name, and that it's only declared once. The
# new path will be the 'res' folder inside the binary directory.
sed -i '/RES_DIR = .*/c\import vidify; RES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(vidify.__file__))), "res")' "vidify/gui/__init__.py"

# Another workaround needed to get libvlc working on Linux
# https://github.com/pyinstaller/pyinstaller/issues/4506
# `os.environ["VLC_PLUGIN_PATH"] = "/usr/lib64/vlc/plugins"` has to be added
# at the end of __init__.py so that VLC can find the needed libraries
# correctly.
echo 'import os; os.environ["VLC_PLUGIN_PATH"] = "/usr/lib64/vlc/plugins"' >> vidify/__init__.py

# Finally running pyinstaller
echo "Running PyInstaller..."
pyinstaller linux.spec --noconfirm || exit 1

echo "Applying post-build patches..."

# Required file not installed by default with Tekore.
mkdir -p dist/vidify/tekore
wget "https://raw.githubusercontent.com/felix-hilden/tekore/master/tekore/VERSION" -O "dist/vidify/tekore/VERSION"

# Saving everything into a zip
echo "Compressing..."
zip -r "vidify-${version}_linux_x86_64.zip" dist/vidify 
