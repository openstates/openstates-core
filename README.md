# openstates-core

This repository contains the Open States data model and scraper backend.

## Links

* [Code of Conduct](https://docs.openstates.org/en/latest/contributing/code-of-conduct.html)
* [Contributing to Open States](https://docs.openstates.org/contributing/)

## Release steps

See [RELASE.md](./RELEASE.md)

## Database Migrations

openstates-core data models may occasionally change, requiring changes to the Open States database in production. Here
are the steps to create and execute a new migration:

* Follow the steps in [Running a Local Database doc](https://docs.openstates.org/contributing/local-database/) to get
  a copy of the database running locally with the prior schema. It is important to develop and test your migration
  locally before executing it on the production DB.
* In most cases, you will auto-generate a migration by first modifying the model file. Make a change to one or more of
  the files in `openstates/data/models`.
* Test the migration locally:
    * Identify the DB connection URL that is accurate to your local database. In most cases, it should
      be: `postgis://openstates:openstates@localhost:5405/openstatesorg`
    * In the repo's root folder, run the `os-dbmakemigrations` command to generate a migration file based on your
      changes: `DATABASE_URL=postgis://openstates:openstates@localhost:5405/openstatesorg poetry run os-dbmakemigrations`
    * Look at the generated migration file in `openstates/data/migrations` and ensure that it looks correct.
    * Execute the migration by running the `os-initdb`
      command: `DATABASE_URL=postgis://openstates:openstates@localhost:5405/openstatesorg poetry run os-initdb`
* Once the migration is verified by local testing, you can execute it against the production DB
    * Identify the DB connection URL that is accurate for the PROD database. This typically should use the same Postgres
      user that owns the tables you want to change. Contact an admin if you need help.
    * Run the `os-initdb` command to
      migrate: `DATABASE_URL=postgis://USERNAME_HERE:PASSWORD_HERE@PROD_DB_HOSTNAME_HERE:5432/openstatesorg poetry run os-initdb`

## Debugging openstates-core code

### Commands that do not integrate with openstates-scrapers

* Install pyenv and correct python version
* Install poetry
* `poetry install`

Example PyCharm config (for `relationships` CLI command):

* Interpeter: the poetry env that you just set up
* Module: `openstates.cli.relationships`
* Parameters: `--log_level=DEBUG us`
* Env vars: `DATABASE_URL=postgres://USERNAME:PASSWORD@DB_HOSTNAME:PORT/openstatesorg`

### Update command / scrapers

There are
[instructions on running a scraper here](https://docs.openstates.org/contributing/scrapers/#running-your-first-scraper)
but what if you want to debug the command that wraps around the scraper code? This
repository's [update CLI module](openstates/cli/update.py)
is the code that accepts parameters and actually executes the scraper (from
[openstates-scrapers](https://github.com/openstates/openstates-scrapers)). Another wrinkle is that the update command
needs to be run inside the context of the `openstates-scrapers` repository, as it will attempt to load in the relevant
scraper for the jurisdiction requested, and that import will fail if you try to run the code here
within `openstates-core`.

Here's a recipe using PyCharm to successfully debug the update command:

#### Requirements to run the scrape/update code natively (not in docker)

* You need the `gdal` library installed on the host system. For me: `sudo apt install gdal-bin python3-gdal`
* `openstates-core` checked out at /home/username/repo/openstates/openstates-core/
* (let's assume you have made some changes in `openstates-core` that you want to test)
* `openstates-scrapers` checked out /home/username/repo/openstates/openstates-scrapers/
* Change directory to /home/username/repo/openstates/openstates-scrapers/
* Install required python version using the `pyenv` utility
* `pip install poetry` (if that python version doesn't already have it)

#### Debugging the scrape/update code natively

* If you have previously installed the `openstates` dependency (eg `openstates-core`), then you need
  to run `poetry remove openstates` to clear that remotely-installed (from pypi) dependency. Each time you make a round
  of changes to `openstates-core`, you will need to remove and then re-add the dependency.
* `poetry add ../openstates-core/` will add the `openstates` dependency from your local filesystem/local checkout
* `poetry install`
* In PyCharm, open the `openstates-scrapers` folder
* In PyCharm, set up a new run config:
    * type: python
    * module: openstates.cli.update
    * parameters: vi bills (or whatever you want to run)
    * working directory: /home/username/repo/openstates/openstates-scrapers/scrapers
* Run the run config in debug mode within PyCharm (eg the one working on `openstates-scrapers`). You can set
  breakpoints within both the scraper code AND in the `openstates-core` code. However you need to open (in PyCharm)
  the copy of `openstates-core` that poetry installed, which probably is in a location like:
  `/home/username/.cache/pypoetry/virtualenvs/openstates-scrapers-93BMrPXy-py3.9/lib/python3.9/site-packages/openstates/cli/update.py`

**Reminder**: when further changes are made to the `openstates-core` package locally, and you want to debug them again,
you need to remove/re-add to update files in `openstates-scrapers`

* Change directory to `/home/username/repo/openstates/openstates-scrapers/`
* `poetry remove openstates`
* `poetry add ../openstates-core/`
* (you will need to re-establish breakpoints in any openstates-core files)
