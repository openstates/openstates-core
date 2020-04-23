# Changelog

## 4.3.0 - 

* add computed fields on Person model
* add computed fields on Bill model
* Person.current_role no longer requires database lookups

## 4.2.0 - April 22 2020

* remove some completely unused fields & models
* add Person current_role, active, current_legislators_with_roles, and search helpers
* remove some unused importer code for Memberships and Posts

## 4.1.1 - April 14 2020

* create executive org on initdb
* allow for dynamic module to handle scrape output instead of JSON dump

## 4.1.0 - April 8 2020

* add os-initdb to get a database with core models in place
* remove old loaddivisions management command
* bugfixes for admin view URLs

## 4.0.1 - April 6 2020

* fix reports tablenames to match old pupa tablenames for now to keep backwards compatibility

## 4.0.0 - April 2 2020

* first release of combined project - essentially without changes

  Prior to 4.0, was two projects:
    * https://github.com/opencivicdata/python-opencivicdata/blob/master/CHANGELOG.md
    * https://github.com/opencivicdata/pupa/blob/master/CHANGELOG.md

  Code in those projects is subject to the license files in the root of the repository.
