#!/bin/sh

set -e
export PYTHONPATH=.;
export DJANGO_SETTINGS_MODULE=openstates_core.test_settings
poetry run django-admin $@
