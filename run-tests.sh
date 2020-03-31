#!/bin/sh
set -e
export PYTHONPATH=.; poetry run pytest --cov pupa --cov-report html --ds=pupa.test_settings --cov-config=.coveragerc $@
coverage report -m
