#!/bin/bash
# Running the tests on docker for multiple Qt bindings.

set -e

export DISPLAY=:99
Xvfb :99 -screen 0 640x480x8 -nolisten tcp &

for binding in "PyQt5" "PySide2"; do
    echo ">> RUNNING TESTS FOR $binding"
    QT_API=$binding python -m unittest
done
