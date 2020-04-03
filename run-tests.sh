#!/bin/sh
set -e
export PYTHONPATH=.; poetry run pytest --cov openstates --cov-report html --ds=openstates.test_settings $@
poetry run coverage report -m
