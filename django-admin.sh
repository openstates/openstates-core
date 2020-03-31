#!/bin/sh

set -e
export PYTHONPATH=.;
export DJANGO_SETTINGS_MODULE=pupa.test_settings
poetry run django-admin $@
