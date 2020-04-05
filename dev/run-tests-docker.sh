#!/bin/bash

export DISPLAY=:99
Xvfb :99 -screen 0 640x480x8 -nolisten tcp &
python -m unittest
