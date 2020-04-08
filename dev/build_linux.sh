#!/bin/sh

set -e
log() { echo -e "\e[36m$*\e[0m"; }
LIBRARIES=("libmpv.so")
log "Building Vidify for Linux"

# This temporary folder will be used to modify Vidify's code automatically
# for different fixes and workarounds.
log "Copying module"
rm -rf vidify
cp -r  ../vidify .

log "Applying pre-build patches"

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

# Calling get_distribution at runtime to check if modules are installed
# doesn't work with PyInstaller, so the is_installed function is overridden:
# https://github.com/pyinstaller/pyinstaller/issues/4795
echo -e \
'def is_installed(*args):
    for s in args:
        if s not in ("python-mpv", "zeroconf", "pydbus", "tekore"):
            return False
    return True' >> vidify/__init__.py


log "Running PyInstaller"

pyinstaller linux.spec --noconfirm || exit 1


log "Applying post-build patches"

# Libraries imported into the files
for library in "${LIBRARIES[@]}"; do
    dir=$(find / -name libmpv.so -print -quit)
    if [ -z "$dir" ]; then
        log "Library $library not found"
        exit 1
    fi
    log "Found $library at $dir"
    cp "$dir" dist/vidify
done

# Required file not installed by default with Tekore.
mkdir -p dist/vidify/tekore
wget -q "https://raw.githubusercontent.com/felix-hilden/tekore/master/tekore/VERSION" -O "dist/vidify/tekore/VERSION"

# Saving everything into a zip inside dist/
version=$(awk '{print $3}' vidify/version.py | tr -d '"')
bin="vidify-v${version}_linux_x86_64.zip"
log "Compressing into $bin"
cd dist
rm -rf "$bin"
zip -q -r "$bin" vidify/*
