#!/bin/bash
# Running the tests on docker for multiple Qt bindings.

set -e

export DISPLAY=:99
Xvfb ${DISPLAY} -screen 0 1280x1024x24 +extension RANDR -nolisten tcp &

for binding in "PyQt5" "PySide2"; do
    echo ">> RUNNING TESTS FOR $binding"
    QT_API=$binding python -m unittest
done
