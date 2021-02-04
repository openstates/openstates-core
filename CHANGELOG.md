# Changelog

## 5.5.1 - February 4 2020

* classifications are now sorted automatically in output JSON

## 5.5.0 - February 3 2020

* EventAgendaItem.order converted to be an integer (migration required)

## 5.4.1 - February 3 2020

* bugfix for openstates/issues#171 where updated_at is churning
  when there are two identical actions

## 5.4.0 - January 20 2020

* update PR senate at-large, 11 senators again

## 5.3.0 - December 30 2020

* update MA district metadata, openstates-core#18
* AZ & NM timezone updates from upstream python-us

## 5.2.1 - November 30 2020

* set Django time zone to UTC by default
* remove unused OrderVoteEvent class

## 5.2.0 - October 28 2020

* add top-level email field to Person

## 5.2.0 - October 28 2020

* add top-level email field to Person

## 5.1.0 - September 23 2020

* disallow bill duplicates that are in opposite chambers
* correct issues with jurisdiction and organization enums
* schema change: add BillDocument and BillVersion classification options
* fix Django 3.1 warnings

## 5.0.3 - September 21 2020

* fix Jurisdiction creation classification

## 5.0.2 - September 14 2020

* fix typo in admin.py for bills
* removed some bad field references

## 5.0.0 - September 14 2020

* merge openstates_metadata into openstates.metadata
* large database cleanup:
  * remove unused fields:
    * BillAbstract.date
    * BillAction.extras
    * BillIdentifier.scheme & note
    * Jurisdiction.feature_flags
    * Membership.label
    * Organization.image, founding_date, dissolution_date
    * Person.summary
    * PersonContactDetail.label
    * Post.start_date & end_date
    * VoteEvent.end_date
    * BillDocumentLink & BillVersionLink.text
    * *.locked_fields
  * add VoteEvent.order

## 4.8.0 - August 21 2020

* remove GIS dependency, alter (unused) EventLocation model accordingly


## 4.7.1 - August 5 2020

* remove person_role_division_id
* fix Person.objects.active()

## 4.7.0 - August 4 2020

* make os-initdb idempotent (and test it!)
* schema change: add Person.current_jurisdiction_id & Person.current_role

## 4.6.0 - July 22 2020

* schema change: allow Jurisdictions to exist without Divisions

## 4.5.1 - June 23 2020

* fix clean_whitespace type issues

## 4.5.0 - June 22 2020

* add 'warn' behavior, now default, to add_version_link/add_document_link
* strip whitespace from all data when being saved
* re-enable VoteEvent classification validation
* start & end date required on legislative_sessions

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
