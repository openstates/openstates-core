#!/bin/sh
set -e
poetry run python creation/write_data.py
black openstates_metadata/data/
poetry run pytest
