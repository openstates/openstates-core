#!/bin/sh

set -e
export PYTHONPATH=.;
export DJANGO_SETTINGS_MODULE=openstates.test_settings
poetry run django-admin $@
