#!/bin/sh
poetry run python creation/write_data.py > ./openstates_metadata/data.py
black openstates_metadata/data.py
poetry run python -m openstates_metadata.data
