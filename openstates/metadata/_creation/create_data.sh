#!/bin/sh
# To run via docker:
#
# docker-compose -f ../openstates.org/docker-compose.yml up -d db
# docker-compose run --rm \
#    --workdir /opt/openstates-core/openstates \
#    --entrypoint metadata/_creation/create_data.sh \
#    -e OVERRIDE_DATABASE_URL=postgis://openstates:openstates@db/test \
#    core
set -e
# Assuming the working directory is openstates-core/openstates
poetry run python metadata/_creation/write_data.py
poetry run black metadata/data/
poetry run pytest --ds=openstates.test_settings -x
