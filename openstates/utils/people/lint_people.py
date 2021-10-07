import re
import datetime
import click
import typing
from pathlib import Path
from dataclasses import dataclass
from collections import defaultdict, Counter
from openstates import metadata
from enum import Enum, auto
from pydantic import ValidationError
from .retire import retire_file
from .general import (
    dump_obj,
    legacy_districts,
    load_municipalities,
)
from ...models.people import Person


class BadVacancy(Exception):
    pass


class PersonType(Enum):
    LEGISLATIVE = auto()
    RETIRED = auto()
    EXECUTIVE = auto()
    MUNICIPAL = auto()


@dataclass
class CheckResult:
    errors: list[str]
    warnings: list[str]
    fixes: list[str]


JURISDICTION_RE = re.compile(
    r"ocd-jurisdiction/country:us/(state|district|territory):\w\w/((place|county):[a-z_]+/)?government"
)

# constant to check for this particular fix
MOVED_TO_RETIRED = "moved to retired"


class Missing:
    pass


def validate_roles(
    person: Person,
    roles_key: str,
    retired: bool = False,
) -> list[str]:
    active = [role for role in getattr(person, roles_key) if role.is_active()]
    if len(active) == 0 and not retired:
        return [f"no active {roles_key}"]
    elif roles_key == "roles" and retired and len(active) > 0:
        return [f"{len(active)} active roles on retired person"]
    elif roles_key == "roles" and len(active) > 1:
        return [f"{len(active)} active roles"]
    return []


def validate_roles_key(
    person: Person,
    person_type: PersonType,
    fix: bool,
) -> CheckResult:
    resp = CheckResult([], [], [])
    role_issues = validate_roles(
        person,
        "roles",
        person_type == PersonType.RETIRED,
    )

    if person_type == PersonType.MUNICIPAL and role_issues == ["no active roles"]:
        # municipals missing roles is a warning to avoid blocking lint
        if fix:
            resp.fixes = [MOVED_TO_RETIRED]
        else:
            resp.warnings.extend(role_issues)
    else:
        resp.errors.extend(role_issues)
    return resp


def validate_offices(person: Person) -> list[str]:
    errors = []
    type_counter: Counter[str] = Counter()
    seen_values: dict[str, str] = {}
    for office in person.offices:
        type_counter[office.classification] += 1
        for key, value in office.dict().items():
            if key == "classification" or not value:
                continue
            # reverse lookup to see if we've used this phone number/etc. before
            location_str = f"{office.classification} {key}"
            if value in seen_values:
                errors.append(
                    f"Value '{value}' used multiple times: {seen_values[value]} and {location_str}"
                )
            seen_values[value] = location_str
    # if type_counter["District Office"] > 1:
    #     errors.append("Multiple district offices.")
    if type_counter["capitol"] > 1:
        errors.append("Multiple capitol offices, condense to one.")
    return errors


def validate_name(person: Person, person_type: PersonType, fix: bool) -> CheckResult:
    """ some basic checks on a persons name """
    errors = []
    fixes = []
    spaces_in_name = person.name.count(" ")
    if spaces_in_name == 1:
        given_cand, family_cand = person.name.split()
        given = person.given_name
        family = person.family_name
        if not given and not family and fix:
            person.given_name = given = given_cand
            person.family_name = family = family_cand
            fixes.append(f"set given_name={given}")
            fixes.append(f"set family_name={family}")
        if not given:
            errors.append(
                f"missing given_name that could be set to '{given_cand}', run with --fix"
            )
        if not family:
            errors.append(
                f"missing family_name that could be set to '{family_cand}', run with --fix"
            )
        # expected_name = f"{given} {family}"
        # if not errors and person.data["name"] != expected_name:
        #     errors.append(f"names do not match given={given} family={family}, but name={person.data['name']}")
    return CheckResult(errors, [], fixes)


def validate_jurisdictions(person: Person, municipalities: list[str]) -> list[str]:
    errors = []
    for role in person.roles:
        try:
            metadata.lookup(jurisdiction_id=role.jurisdiction)
        except KeyError:
            if role.jurisdiction not in municipalities:
                errors.append(f"{role.jurisdiction} is not a valid jurisdiction_id")
    return errors


_EXPECTED_DISTRICTS_TYPE = dict[str, dict[str, int]]
_ACTUAL_DISTRICTS_TYPE = defaultdict[str, defaultdict[str, list[str]]]


def get_expected_districts(
    settings: dict[str, dict], abbr: str
) -> _EXPECTED_DISTRICTS_TYPE:
    expected = {}

    state = metadata.lookup(abbr=abbr)
    for chamber in state.chambers:
        chtype = (
            "legislature"
            if chamber.chamber_type == "unicameral"
            else chamber.chamber_type
        )
        expected[chtype] = {
            district.name: district.num_seats for district in chamber.districts
        }

    # remove vacancies
    vacancies = settings.get(abbr, {}).get("vacancies", [])
    if vacancies:
        click.secho(f"Processing {len(vacancies)} vacancies:")
    for vacancy in vacancies:
        if datetime.date.today() < vacancy["vacant_until"]:
            expected[vacancy["chamber"]][str(vacancy["district"])] -= 1
            click.secho(
                "\t{chamber}-{district} (until {vacant_until})".format(**vacancy),
                fg="green",
            )
        else:
            click.secho(
                "\t{chamber}-{district} expired {vacant_until} remove & re-run".format(
                    **vacancy
                ),
                fg="red",
            )
            raise BadVacancy()

    return expected


def compare_districts(
    expected: _EXPECTED_DISTRICTS_TYPE, actual: _ACTUAL_DISTRICTS_TYPE
) -> list[str]:
    errors = []

    if expected.keys() != actual.keys():
        errors.append(f"expected districts for {expected.keys()}, got {actual.keys()}")
        return errors

    for chamber in expected:
        expected_districts = set(expected[chamber].keys())
        actual_districts = set(actual[chamber].keys())
        for district in sorted(expected_districts - actual_districts):
            if expected[chamber][district]:
                errors.append(f"missing legislator for {chamber} {district}")
        for district in sorted(actual_districts - expected_districts):
            errors.append(f"extra legislator for unexpected seat {chamber} {district}")
        for district in sorted(actual_districts & expected_districts):
            if len(actual[chamber][district]) < expected[chamber][district]:
                errors.append(f"missing legislator for {chamber} {district}")
            if len(actual[chamber][district]) > expected[chamber][district]:
                people = "\n\t".join(actual[chamber][district])
                errors.append(
                    f"extra legislator for {chamber} {district}:\n\t" + people
                )
    return errors


class Validator:
    def __init__(self, abbr: str, settings: dict, fix: bool, save_all: bool):
        self.fix = fix
        self.save_all = save_all
        self.expected = get_expected_districts(settings, abbr)
        self.errors: defaultdict[str, list[str]] = defaultdict(list)
        self.warnings: defaultdict[str, list[str]] = defaultdict(list)
        self.fixes: defaultdict[str, list[str]] = defaultdict(list)
        # role type -> district -> filename
        self.active_legislators: defaultdict[
            str, defaultdict[str, list[str]]
        ] = defaultdict(lambda: defaultdict(list))
        # field name -> value -> filename
        self.duplicate_values: defaultdict[
            str, defaultdict[str, list[str]]
        ] = defaultdict(lambda: defaultdict(list))
        self.legacy_districts = legacy_districts(abbr=abbr)
        self.municipalities = [m["id"] for m in load_municipalities(abbr=abbr)]
        for m in self.municipalities:
            if not JURISDICTION_RE.match(m):
                raise ValueError(f"invalid municipality id {m}")

    def process_validator_result(
        self,
        validator_func: typing.Callable[[Person, PersonType, bool], CheckResult],
        person: Person,
        person_type: PersonType,
        original_filename: Path,
    ) -> None:
        result = validator_func(person, person_type, self.fix)
        self.errors[original_filename.name].extend(result.errors)
        self.warnings[original_filename.name].extend(result.warnings)
        if result.fixes:
            self.fixes[original_filename.name].extend(result.fixes)
            dump_obj(person, filename=original_filename)

    def validate_person(
        self,
        data: dict[str, typing.Any],
        filename: Path,
        person_type: PersonType,
    ) -> None:
        print_filename = filename.name
        try:
            person = Person(**data)
            self.errors[print_filename] = []
        except ValidationError as ve:
            self.errors[print_filename] = [
                f"  {'.'.join(str(l) for l in error['loc'])}: {error['msg']}"
                for error in ve.errors()
            ]
            # if we couldn't create a valid person, bail now
            return

        uid = person.id.split("/")[1]
        if uid not in print_filename:
            self.errors[print_filename].append(f"id piece {uid} not in filename")

        self.errors[print_filename].extend(
            validate_jurisdictions(person, self.municipalities)
        )

        # looser validation for upstream-maintained unitedstates.io data
        if "/us/legislature" not in str(filename):
            self.errors[print_filename].extend(validate_offices(person))

        self.process_validator_result(validate_roles_key, person, person_type, filename)
        self.process_validator_result(validate_name, person, person_type, filename)

        if person_type == PersonType.RETIRED:
            self.errors[print_filename].extend(self.validate_old_district_names(person))

        # check duplicate IDs
        self.duplicate_values["openstates"][person.id].append(print_filename)
        for scheme, value in person.ids.dict().items():
            if value:
                self.duplicate_values[scheme][value].append(print_filename)
        for ident in person.other_identifiers:
            self.duplicate_values[ident.scheme][ident.identifier].append(print_filename)

        # update active legislators
        if person_type == PersonType.LEGISLATIVE:
            role_type = district = None
            for role in person.roles:
                if role.is_active():
                    role_type = role.type
                    district = role.district
                    break
            self.active_legislators[str(role_type)][str(district)].append(
                print_filename
            )

        # special case for the auto-retirement fix
        if MOVED_TO_RETIRED in self.fixes[print_filename]:
            retire_file(filename)

        if self.save_all:
            # save person if save_all, will re-order fields/etc.
            click.secho(f"re-saving {filename}", fg="green")
            dump_obj(person, filename=filename)

    def validate_old_district_names(self, person: Person) -> list[str]:
        errors = []
        for role in person.roles:
            if (
                role.district
                and role.district not in self.expected[role.type]
                and role.district not in self.legacy_districts[role.type]
            ):
                errors.append(f"unknown district name: {role.type} {role.district}")
        return errors

    def check_duplicates(self) -> list[str]:
        """
        duplicates should already be stored in self.duplicate_values
        this method just needs to turn them into errors
        """
        errors = []
        for key, values in self.duplicate_values.items():
            for value, instances in values.items():
                if len(instances) > 1:
                    if len(instances) > 3:
                        instance_str = ", ".join(instances[:3])
                        instance_str += " and {} more...".format(len(instances) - 3)
                    else:
                        instance_str = ", ".join(instances)
                    errors.append(f'duplicate {key}: "{value}" {instance_str}')
        return errors

    def print_validation_report(self, verbose: bool) -> int:  # pragma: no cover
        error_count = 0

        for fn, errors in self.errors.items():
            warnings = self.warnings[fn]
            fixes = self.fixes[fn]
            if errors or warnings or fixes:
                click.echo(fn)
                for fix in fixes:
                    click.secho(" " + fix, fg="green")
                for err in errors:
                    click.secho(" " + err, fg="red")
                    error_count += 1
                for warning in warnings:
                    click.secho(" " + warning, fg="yellow")
            if not errors and verbose > 0:
                click.secho(fn + " OK!", fg="green")

        for err in self.check_duplicates():
            click.secho(err, fg="red")
            error_count += 1

        errors = compare_districts(self.expected, self.active_legislators)
        for err in errors:
            click.secho(err, fg="red")
            error_count += 1

        return error_count
