#!/bin/sh
poetry run python creation/write_data.py
black openstates_metadata/data/
poetry run python -m openstates_metadata.data.nc
