#!/bin/sh
# Script for automatic formatting of code and linting

set -e

echo ">> Formatting"
python -m black .
echo ">> Sorting imports"
python -m isort .
echo ">> Running linter"
python -m flake8 .
