#!/bin/sh
set -e
export PYTHONPATH=.; poetry run pytest --cov pupa --cov-report html --ds=pupa.tests.django_settings --cov-config=.coveragerc $@
coverage report -m
