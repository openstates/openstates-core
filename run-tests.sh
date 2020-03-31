#!/bin/sh
set -e
export PYTHONPATH=.; py.test --cov opencivicdata --ds=opencivicdata.tests.test_settings --cov-report html --cov-config=.coveragerc
export PYTHONPATH=.; pytest --cov pupa --cov-report html --ds=pupa.tests.django_settings
coverage report -m
