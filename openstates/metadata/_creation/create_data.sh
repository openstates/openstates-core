#!/bin/sh
set -e
poetry run python creation/write_data.py
black metadata/data/
poetry run pytest
