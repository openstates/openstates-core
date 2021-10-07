#!/usr/bin/env python
import typing
import os
import yaml
from pathlib import Path
from datetime import datetime
from ... import metadata
from ...models.people import Person


def add_vacancy(person: Person, until: datetime) -> None:
    with open("settings.yml") as f:
        settings = yaml.safe_load(f)
    last_role = person.roles[-1]
    abbr = metadata.lookup(jurisdiction_id=last_role.jurisdiction).abbr.lower()
    if abbr not in settings:
        settings[abbr] = {"vacancies": []}
    settings[abbr]["vacancies"].append(
        {
            "chamber": last_role.type,
            "district": last_role.district,
            "vacant_until": until.date(),
        }
    )
    with open("settings.yml", "w") as f:
        yaml.safe_dump(settings, f)


def retire_person(
    person: Person,
    end_date: str,
    reason: typing.Optional[str] = None,
    death: bool = False,
) -> tuple[Person, int]:
    num = 0
    for role in person.roles:
        if role.is_active():
            role.end_date = end_date
            if reason:
                role.end_reason = reason
            num += 1

    if death:
        person.death_date = end_date

    # remove old offices
    person.offices = []

    return person, num


def retire_file(filename: typing.Union[Path, str]) -> str:  # pragma: no cover
    if isinstance(filename, Path):
        filename = str(filename)
    new_filename = filename.replace("/legislature/", "/retired/").replace(
        "/municipalities/", "/retired/"
    )
    os.renames(filename, new_filename)
    return new_filename
