#!/bin/sh

set -e
export PYTHONPATH=.;
export DJANGO_SETTINGS_MODULE=pupa.tests.django_settings
poetry run django-admin $@
