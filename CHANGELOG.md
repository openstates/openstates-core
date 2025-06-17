# Changelog

## 6.24.0 - Jun 17, 2025
* Incrementally saving scrape output to GCS, --archive turned on. Uses a default interval of 15 minutes to upload a JSONL file of 
  by data class. Data class can be jurisdiction, organization, bill, event and vote event. 

## 6.23.0 - May 21, 2025
* Introduces --http-resilience flag for the os-update command which runs a scraper with techniques to avoid getting
  disconnected from a source server.

## 6.22.3 - May 14, 2025
* Use DAG run start time for archiving scrape output

## 6.22.2 - Apr 25, 2025
* Bug fix due to metadata error during import

## 6.22.1 - Apr 24, 2025
* Add Forward Party as a political party option
* Update PR senate to 28 seats incl 12 at-large
* Update PR senate to 53 seats incl 13 at-large
* Update ND house district to merge 9A and 9B into district 9
* Stop restricting multiple capitol offices

## 6.22.0 - Apr 22, 2025
* Add metadata to scraper output

## 6.21.6 - Apr 21, 2025
* Add informal passage to bill action classification

## 6.21.5 - Apr 9, 2025
* Add to Docker workflow to publish to internal repo as well

## 6.21.4 - Mar 11, 2025
* Remove extra whitespace from query value

## 6.21.3 - Mar 3, 2025

* Purge Committees to database by default

## 6.21.2 - Mar 3, 2025

* Catch Django Settings already configures exception

## 6.21.1 - Mar 1, 2025

* Update people repo cli usage

## 6.21.0 - Feb 28, 2025

* Install git for gitPython dependencies usage

## 6.20.16 - Feb 26, 2025

* Add CLI script to ingest into database from people repo 

## 6.20.15 - Feb 14, 2025

* Committee yaml-to-database cli should be able to update committee name 

## 6.20.14 - Jan 27, 2025

* Allow duplicate items to be imported in import via new runtime flag --allow_duplicates

## 6.20.13 - Dec 27, 2024

* Sanitize phone number for US people scrape.

## 6.20.12 - Nov 22, 2024

* Use transformers to trim incoming strings at import that are too long for DB columns:
    * Bill: document note, version note
    * Event: media note

## 6.20.11 - Nov 15, 2024

* This release was yanked. It involved a database migration that operationally failed,
  and was reverted.

## 6.20.10 - Nov 7, 2024

* Add additional log info re: archiving scrape files to cloud storage

## 6.20.9 - Nov 4, 2024

* Fix bug with import caused by newish "extras" field on scraper

## 6.20.8 - Oct 18, 2024

* Improve resolve bill to capture at least the most recent session

## 6.20.7 - Oct 10, 2024

* Fix matching committee organizations when chamber is specified for an organizational bill sponsor

## 6.20.6 - Sept 18, 2024

* Add steps to publish lightweight openstates-metadata

## 6.20.5 - Sept 18, 2024

* Improve Event to Person matching

## 6.20.4 - Sept 16, 2024

* Add Chamber on Bill Sponsorship matches for people
* Improve Event to Bill matching for Events on last day of session

## 6.20.3 - Aug 27, 2024

* Improve query for searching committee other_names

## 6.20.2 - Aug 14, 2024

* Prevent failure in Google Cloud Storage archiving from failing a scrape/update operation

## 6.20.1 - Aug 2, 2024

* Fix permissions issue caused by slightly wrong usage of GCP storage client code

## 6.20.0 - Aug 1, 2024

* Adds support for --archive flag on os-update to archive a full scrape to google cloud storage bucket

## 6.19.3 - Jul 8, 2024

* Add instructions on DB migrations to docs
* Change schema to fix two DB issues:
    * Event Document `note` changed to Text type to avoid character limit errors
    * Vote Event `dedupe_key` index added to improve performance on Vote Event lookups during import

## 6.19.2 - Jun 7, 2024

* Turn off archiving processed realtime bills by default.

## 6.19.0 - April 5, 2024

* Adds a new CLI tool that can be called to resolve unresolved bill-to-bill relationships in the openstates DB

## 6.18.5 - March 29, 2024

* other_name in committee matching
* swap getargspec for getfullargspec on Update

## 6.18.4 - March 25, 2024

* Rollback on committee matching

## 6.18.3 - March 25, 2024

* Add other_names to committee matching for Event Imports

## 6.18.2

* Maine (ME): add a tribal representative district to the jurisdiction metadata

## 6.18.1 - January 24, 2024

* Stop validating the repeated use of the same phone number in People offices data

## 6.18.0 - January 24, 2024

* People: add distinct mailing classification options (district-mail, capitol-mail) and home classification to offices
* Docs: Add debug instructions for the update command by @jessemortenson in #119

## 6.17.9 - October 26, 2023

* allow postimport hook to be skipped in os-update command

## 6.17.8 - October 16, 2023

* set application_name for better performance monitoring

## 6.17.5 - August 9, 2023

* Add new bill statuses to validation

## 6.17.4 - August 2, 2023

* Small territory fixes

## 6.17.3 - August 1, 2023

* update pyyaml dependency

## 6.17.2 - August 1, 2023

* Support additional territories in db init

## 6.17.0 - July 14, 2023

* Add additional US territory support#113

## 6.16.5 - May 16, 2023

* update logs on import

## 6.16.4 - April 12, 2023

* check abbr on division creation

## 6.16.3 - April 12, 2023

* change name lookup

## 6.16.2 - April 11, 2023

* Correct initdb for ZA

## 6.16.1 - April 11, 2023

* Init metadata for ZA

## 6.16.0 - April 7, 2023

* Add metadata for ZA

## 6.15.4 - February 21, 2023

* Update bill action classification options

## 6.15.3 - February 14, 2023

* Update MA metadata

## 6.15.2.3 - February 13, 2023

* Change to force deploy

## 6.15.2.2 - February 13, 2023

* Bump version correctly

## 6.15.2.1 - February 13, 2023

* Fix CI bug

## 6.15.2 - February 13, 2023

* Update legacy district ids & seats
* Add database migrations & metadata updates to release steps

## 6.15.1 - February 6, 2023

* Fix boto3 library usage for realtime consumption
* Add CLI tool for manual JSON schema validation

## 6.15.0 - February 1, 2023

* Updated Districts for NH

## 6.14.9 - January 31, 2023

* Updated Districts for PR, MD, MA, NH, ID, ND, VT

## 6.14.8 - January 30, 2023

* Realtime Bills Metrics Update

## 6.14.7 - January 30, 2023

* Updated Districts for MA and VT

## 6.14.6 - January 25, 2023

* skip bad tags

## 6.14.3.1 - January 25, 2023

* revert nomination event type

## 6.14.2 - January 24, 2023

* add nomination as valid event type

## 6.14.1 - January 20, 2023

* update to metadata for MD

## 6.14.0 - January 11, 2023

* update to metadata for MA, MD, ND, NH, US, VT, WV, WY

## 6.13.9 - January 10, 2023

* add SQS for batching

## 6.13.8 - January 9, 2023

* update us legacy districts

## 6.13.7 - January 9, 2023

* update us district numbers

## 6.13.5 - January 4, 2023

* check for congress bio info existing before assigning values

## 6.13.4 - January 3, 2023

* properly handle bad UUIDs in event objects

## 6.13.3 - December 28, 2022

* session key bug fix

## 6.13.2 - December 22, 2022

* Actually set timeout on JWT tokens
* clean up instrumentation endpoint

## 6.13.1 - December 21, 2022

* fix import bug

## 6.13.0 - December 20, 2022

* emit stat data as scrapers run

## 6.12.0 - December 15, 2022

* adds realtime bill yield

## 6.11.1 - July 11, 2022

* update dependency
* decrease size of dockerfile

## 6.11.0 - June 30, 2022

* update dependency
* add additional parties for NY senate
* allow returning None objects in scrapes
* skip objects with unresolved ID error

## 6.10.12 - April 25, 2022

* update django dependency

## 6.10.11 - March 14, 2022

* FL: Fix text extraction
* move scrapelib dependency to Civic Eagle forked repo

## 6.10.10 - March 8, 2022

* add wikidata to people ids

## 6.10.9 - February 16 2022

* test for rylie

## 6.10.8 - February 10 2022

* loosen version requirements for spatula

## 6.10.7 - February 3 2022

* fix https://github.com/openstates/issues/issues/598, committees with duplicate names

## 6.10.6 - January 31 2022

* update click dependency

## 6.10.5 - January 21 2022

* US text extraction enabled
* fix for openstates/issues#608

## 6.10.4 - January 11 2022

* fix typo in 6.10.3 release

## 6.10.3 - January 11 2022

* fix for subcommittee memberships not being ignored on person import
* special case fix for extracting bill text from California (openstates/issues#147)

## 6.10.2 - January 3 2022

* fixes for people merging
* handle null committees in committee merge/scrape
* allow executives to have inactive roles too for linting purposes

## 6.10.1 - December 20 2021

* add committees to os-scrape command
* improve committee merging

## 6.10.0 - December 15 2021

* add prototype os-scrape command to help with people updates
* people model fix for empty URL validation
* people model fix for new suffixes
* add --reset-offices flag for people merging when office data has changed significantly
* lots of improvements to os-people merge's automation

## 6.9.2 - November 29 2021

* improve committee membership validation
* add migration to os-initdb

## 6.9.1 - November 17 2021

* fix for bad phone numbers in update-us

## 6.9.0 - November 9 2021

* OSEP #2: add citation support to Bill
* several test fixes for OS committee changes
* fix for update-us

## 6.8.2 - November 8 2021

* os-committee linting improvements
* os-committee merge avoids duplicates

## 6.8.1 - November 4 2021

* fix for circular import in openstates.metadata

## 6.8.0 - October 26 2021

* OSEP #8: add LegislativeSession.active flags
* running a scraper without a session will now run active sessions instead of "latest"
* removal of BillScraper.latest_session in favor of new session injection
* replace scrape.Jurisdiction with scrape.State, which was formerly in scrapers.utils

## 6.7.0 - October 13 2021

* remove PersonContactDetail entirely, completing OSEP #6

## 6.6.1 - October 12 2021

* bugfix for openstates.data django app with new PersonOffice model
* bugfix for us-to-yaml addresses missing names

## 6.6.0 - October 8 2021

* implement core parts of OSEP #6: switch to Person.offices from Person.contact_details
* bugfixes for committee merge with joint committees & case-insensitive matching

## 6.5.3 - September 24 2021

* bugfix for EventImporter.postimport being called after bill-only scrapes

## 6.5.2 - September 23 2021

* bugfix for duplicates on Event importer
* fix for bill matching on Event importer
* speed up imports when there are no bills in import

## 6.5.1 - September 22 2021

* import fix for committee_id on scraped events
* enable import of events by default in os-update

## 6.5.0 - September 21 2021

* allow raising `EmptyScrape` to end a scrape without 'no objects returned' error
* added `upstream_id` to Event model
* add classification parameter to `Event.add_document`
* fix up `Event.add_media_link` parameters to be uniform (including classification)
* added `Event.add_bill` helper method
* `os-people-to-yaml` is now part of `os-people merge`
* Events imports now include soft-deletion of events that are not included in latest scrape

## 6.4.1 - August 19 2021

* committee merge bugfix for parent committees
* normalize whitespace in committee names/members
* add --fix flag to committee lint

## 6.4.0 - August 2 2021

* fix os-us-to-yaml phone numbers
* added latest_bill_update and latest_people_update to Jurisdiction table
  (these fields are now automatically updated when os-update or os-people
  update the relevant tables)
* moved openstates.reports into openstates.data

## 6.3.4 - August 2 2021

* fix os-us-to-yaml with no office details

## 6.3.3 - August 1 2021

* fix for OS_PEOPLE_DIRECTORY setting detection
* fix committee import to include extras

## 6.3.2 - July 20 2021

* stop auto-purging committees

## 6.3.1 - July 19 2021

* add linting check for committee homepages
* committees will always have classification in file
* fix committee linting/import/etc. to set parent key to an ocd-organization ID

## 6.3.0 - July 14 2021

* fix for committee parent/subcommittee in ScrapeCommittee
* committees in os-us-to-yaml
* committees linting includes warnings now

## 6.2.1 - July 7 2021

* refactor openstates.people into openstates.models and openstates.utils

## 6.2.0 - July 5 2021

* refactor openstates.people into openstates.models and openstates.utils

## 6.1.0 - July 2 2021

* committee database imports
* add support for scraping subcommittees
* set charset on CSV uploads

## 6.0.3 - June 3 2021

* fix for ScrapeCommittee add_link/add_source

## 6.0.2 - June 2 2021

* improved use of typing, which will now be enforced going forward
* added --save-all flag to os-people lint
* us legislators script fixes
* fix boto being initialized if not used

## 6.0.1 - May 25 2021

* bugfix for os-people's get_all_abbreviations()

## 6.0.0 - May 25 2021

* bump to Python 3.9
* move openstates/text-extraction repository into openstates.fulltext
* move openstates/people tools into openstates.cli and openstates.people

## 5.11.1 - May 10 2021

* add obsolete US districts to metadata

## 5.11.0 - May 10 2021

* add US territories to metadata

## 5.10.0 - April 27 2021

* backwards incompatible migration needed: Organization fields JSON-ized (part of OSEP #4)
* updates to work with Django 3.2
* warnings on duplicate sponsors

## 5.9.4 - April 13 2021

* case-insensitive person matching

## 5.9.3 - April 12 2021

* improvement for person matching to restrict to legislative roles

## 5.9.2 - April 12 2021

* fix for organization sponsors on import

## 5.9.1 - April 12 2021

* fix for get_seen_sessions error introduced in 5.9.0

## 5.9.0 - April 12 2021

* improved Person resolution in importers
* added typing to openstates.metadata
* added typing to openstates.importers

## 5.8.2 - April 7 2021

* fix for microsecond replacement on date

## 5.8.1 - April 6 2021

* fix_bill_id fixed for US bills
* strip microseconds from datetimes in JSON output

## 5.8.0 - April 5 2021

* remaining implementation of OSEP #5
    * remove pupa_id backwards compatibility
    * migration: drop reports.Identifier
* Add veto and veto-override vote classifications

## 5.7.1 - April 5 2021

* bugfix for typo in scrape schema in 5.7.0

## 5.7.0 - April 2 2021

* Implementation of OSEP #5
    * migration: added dedupe_key to replace pupa_id
    * added dedupe_key to replace pupa_id in scrape as well
    * alter import logic to stop using reports.Identifier

## 5.6.0 - March 23 2021

* add support for US jurisdiction

## 5.5.3 - February 10 2021

* add 'related' as additional bill relation type (openstates/issues#181)

## 5.5.2 - February 8 2021

* subjects are now sorted automatically in output JSON

## 5.5.1 - February 4 2021

* classifications are now sorted automatically in output JSON

## 5.5.0 - February 3 2021

* EventAgendaItem.order converted to be an integer (migration required)

## 5.4.1 - February 3 2021

* bugfix for openstates/issues#171 where updated_at is churning
  when there are two identical actions

## 5.4.0 - January 20 2021

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
