#!/bin/sh
set -e
export PYTHONPATH=.; uv run pytest --cov openstates --cov-report html --ds=openstates.test_settings $@
uv run coverage report -m
