# Changelog

## 4.5.0 - WIP

* add 'warn' behavior, now default, to add_version_link/add_document_link

## 4.4.3 - June 16 2020

* bugfix for member_of with post

## 4.4.2 - May 1 2020

* bugfix for os-update importer crashing

## 4.4.1 - April 30 2020

* bugfix for Person.member_of returning duplicates

## 4.4.0 - April 29 2020

* simplify org and person import code as part of refactor
* add Person.current_state
* alter Bill computed fields to be null if unset
* update Person queries to make use of new computed fields
* bugfix for os-update-computed
* bugfix for LegislativeSession in admin

## 4.3.2 - April 25 2020

* improve update computed command
* add BaseImporter.update_computed_fields
* fix return code

## 4.3.1 - April 23 2020

* make new fields temporarily nullable
* fix updated-computed init_django bug

## 4.3.0 - April 23 2020

* add computed fields on Person model
* add computed fields on Bill model
* Person.current_role no longer requires database lookups
* add os-updated-computed command that updates computed fields

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
