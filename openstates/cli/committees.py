import re
import sys
import json
import uuid
import typing
from functools import lru_cache
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from collections import defaultdict
import click
import yaml
from django.db import transaction  # type: ignore
from yaml.representer import Representer
from pydantic import ValidationError
from ..metadata import lookup
from ..utils.django import init_django  # type: ignore
from ..utils.people import get_data_path, get_all_abbreviations
from ..utils.people.to_database import CancelTransaction
from ..models.committees import Committee, ScrapeCommittee
from ..models.people import Person

yaml.SafeDumper.add_representer(defaultdict, Representer.represent_dict)
yaml.SafeDumper.add_multi_representer(Enum, Representer.represent_str)  # type: ignore


@dataclass
class DirectoryMergePlan:
    names_to_add: set[str]
    names_to_remove: set[str]
    same: int
    to_merge: list[tuple[Committee, ScrapeCommittee]]


class PersonMatcher:
    def __init__(self, abbr: str, directory: typing.Optional[Path] = None):
        self.abbr = abbr
        # chamber -> name piece -> id set
        self.current_people: dict[str, dict[str, set[str]]] = {
            "upper": {},
            "lower": {},
            "legislature": {},
        }
        self.all_ids: set[str] = set()

        # allow directory override for testing purposes
        if not directory:
            directory = get_data_path(abbr) / "legislature"

        # read in people with current roles
        for filename in directory.glob("*.yml"):
            person: Person = Person.load_yaml(filename)
            chamber = ""
            for role in person.roles:
                if role.is_active():
                    chamber = role.type
                    break
            self.add_name(chamber, person.name, person.id)
            if person.family_name:
                self.add_name(chamber, person.family_name, person.id)
            for name in person.other_names:
                self.add_name(chamber, name.name, person.id)

    def add_name(self, chamber: str, name_piece: str, id_: str) -> None:
        name_piece = name_piece.lower()
        self.all_ids.add(id_)
        if name_piece in self.current_people[chamber]:
            self.current_people[chamber][name_piece].add(id_)
        else:
            self.current_people[chamber][name_piece] = {id_}
        # add to legislature too
        if chamber != "legislature":
            self.add_name("legislature", name_piece, id_)

    @lru_cache(500)
    def match(self, chamber: str, name: str) -> typing.Optional[str]:
        name = name.lower()
        candidates = self.current_people[chamber].get(name, None)
        if not candidates:
            click.secho(
                f"  no candidates while attempting to match {chamber} {name}",
                fg="yellow",
            )
            return None
        elif len(candidates) == 1:
            return list(candidates)[0]
        else:
            click.secho(
                f"  multiple candidates while attempting to match {chamber} {name}",
                fg="yellow",
            )
            return None

    def id_exists(self, id_: str) -> bool:
        return id_ in self.all_ids


@lru_cache(5)
def _parent_lookup(jurisdiction_id: str, chamber: str, parent: str) -> str:
    from openstates.data.models import Organization

    if parent:
        return parent
    else:
        return Organization.objects.get(
            jurisdiction_id=jurisdiction_id, classification=chamber
        ).id


def committee_to_db(com: Committee) -> tuple[bool, bool, bool]:
    from openstates.data.models import Organization, Membership

    updated = False
    name_changed = False

    db_com, created = Organization.objects.get_or_create(
        id=com.id,
        jurisdiction_id=com.jurisdiction,
        parent_id=_parent_lookup(com.jurisdiction, com.chamber, com.parent),
        classification=com.classification,
        defaults=dict(name=com.name, extras=com.extras),
    )

    if db_com.name != com.name:
        updated = True
        name_changed = True
        db_com.name = com.name

    if db_com.extras != com.extras:
        updated = True
        db_com.extras = com.extras

    for key_name in ("links", "sources", "other_names"):
        list_json = [n.dict() for n in getattr(com, key_name)]
        if list_json != getattr(db_com, key_name):
            setattr(db_com, key_name, list_json)
            updated = True

    existing_members = {
        (m.person_id, m.person_name, m.role)
        for m in db_com.memberships.all().select_related("person")
    }
    scraped_members = {(m.person_id, m.name, m.role) for m in com.members}

    if existing_members != scraped_members:
        # replace members
        updated = True
        new_memberships = [
            Membership(
                role=m.role,
                person_name=m.name,
                person_id=m.person_id,
                organization=db_com,
            )
            for m in com.members
        ]
        db_com.memberships.all().delete()
        Membership.objects.bulk_create(new_memberships)

    if updated:
        db_com.save()
        # don't set updated to true in return if created
        if created:
            updated = False
    return created, updated, name_changed


def merge_lists(orig: list, new: list, key_attr: str) -> list:
    """merge two lists based on a unique property"""
    combined = []
    new_by_key = {getattr(item, key_attr): item for item in new}
    seen = set()
    # add original items, or their replacements if present
    for item in orig:
        key = getattr(item, key_attr)
        if key in seen:
            continue
        seen.add(key)
        if key in new_by_key:
            combined.append(new_by_key[key])
        else:
            combined.append(item)
    # add new items
    for key, item in new_by_key.items():
        if key not in seen:
            combined.append(item)
    return combined


class CommitteeDir:
    def __init__(
        self,
        abbr: str,
        raise_errors: bool = True,
        directory: typing.Optional[Path] = None,
    ):
        self.abbr = abbr
        # allow overriding directory explicitly, useful for testing
        self.directory = directory if directory else get_data_path(abbr) / "committees"
        # chamber -> name -> Committee
        self.coms_by_parent_and_name: defaultdict[str, dict[str, Committee]] = (
            defaultdict(dict)
        )
        self.errors = []
        # person matcher will be prepared if/when needed
        self.person_matcher: typing.Optional[PersonMatcher] = None

        # make sure a committees dir exists
        self.directory.mkdir(parents=True, exist_ok=True)

        for filename in self.directory.glob("*.yml"):
            try:
                com: Committee = Committee.load_yaml(filename)
                self.coms_by_parent_and_name[com.parent or com.chamber][com.name] = com
            except ValidationError as ve:
                if raise_errors:
                    raise
                self.errors.append((filename, ve))

    def merge_committees(self, orig: Committee, new: ScrapeCommittee) -> Committee:
        # need new parent id
        new_parent_id = None
        if new.parent:
            new_parent_id = self.coms_by_parent_and_name[new.chamber][new.parent].id

        # disallow merge of these, likely error & unclear what should happen
        if orig.chamber != new.chamber:
            raise ValueError("cannot merge committees with different chambers")
        if orig.parent != new_parent_id:
            print(orig)
            print(new_parent_id)
            print(new)
            raise ValueError("cannot merge committees with different parents")
        if orig.classification != new.classification:
            raise ValueError("cannot merge committees with different classifications")
        # TODO: jurisdiction isn't yet set on ScrapeCommittee... do we need another check here?

        merged = Committee(
            id=orig.id,  # id stays constant
            chamber=orig.chamber,
            parent=orig.parent,
            classification=orig.classification,
            jurisdiction=orig.jurisdiction,
            name=new.name,  # name can be updated
            sources=merge_lists(orig.sources, new.sources, "url"),
            links=merge_lists(orig.links, new.links, "url"),
            other_names=merge_lists(orig.other_names, new.other_names, "name"),
            members=merge_lists(orig.members, new.members, "name"),
            extras=orig.extras | new.extras,
        )
        return merged

    def print_warnings(self) -> None:
        unmatched_names = set()
        for coms_for_chamber in self.coms_by_parent_and_name.values():
            for com in coms_for_chamber.values():
                has_homepage = "homepage" in [link.note for link in com.links]
                if com.classification == "committee" and not has_homepage:
                    click.secho(f"{com.name} does not have homepage link", fg="yellow")
                for membership in com.members:
                    if not membership.person_id:
                        unmatched_names.add(membership.name)

        if unmatched_names:
            click.secho(f"{len(unmatched_names)} unmatched legislators:", fg="yellow")
            for name in unmatched_names:
                click.secho(f"    {name}", fg="yellow")
            click.secho("try running with --fix", fg="yellow")

    def get_new_filename(self, obj: Committee) -> str:
        id = obj.id.split("/")[1]
        name = re.sub(r"\s+", "-", obj.name)
        name = re.sub(r"[^a-zA-Z-]", "", name)
        return f"{obj.chamber}-{name}-{id}.yml"

    def get_filename_by_id(self, com_id: str) -> Path:
        if com_id.startswith("ocd-organization"):
            com_id = com_id.split("/")[1]
        assert len(com_id) == 36
        files = list(self.directory.glob(f"*{com_id}.yml"))
        if len(files) == 1:
            return files[0]
        else:
            raise FileNotFoundError()

    def get_filename_by_name(self, parent: str, name: str) -> Path:
        try:
            com = self.coms_by_parent_and_name[parent][name]
        except KeyError:
            raise FileNotFoundError()
        return self.get_filename_by_id(com.id)

    def save_committee(self, committee: Committee) -> None:
        # try to use id's existing filename if possible
        try:
            filename = self.get_filename_by_id(committee.id)
        except FileNotFoundError:
            filename = self.directory / self.get_new_filename(committee)

        with open(filename, "w") as f:
            yaml.dump(
                committee.to_dict(),
                f,
                default_flow_style=False,
                Dumper=yaml.SafeDumper,
                sort_keys=False,
            )

    def add_committee(self, committee: ScrapeCommittee) -> None:
        parent_id: typing.Optional[str]
        # parent name needs to be converted to ID
        if committee.parent:
            parent_id = self.coms_by_parent_and_name[committee.chamber][
                committee.parent
            ].id
        else:
            parent_id = None
        # convert a ScrapeCommittee to a committee by giving it an ID
        full_com = Committee(
            id=f"ocd-organization/{uuid.uuid4()}",
            jurisdiction=lookup(abbr=self.abbr).jurisdiction_id,
            parent=parent_id,
            **committee.dict(exclude={"parent"}),
        )
        self.coms_by_parent_and_name[committee.parent or committee.chamber][
            committee.name
        ] = full_com
        self.save_committee(full_com)

    def ingest_scraped_json(self, input_dir: str) -> list[ScrapeCommittee]:
        if not self.person_matcher:
            self.person_matcher = PersonMatcher(self.abbr)

        scraped_data = []
        for filename in Path(input_dir).glob("*"):
            with open(filename) as file:
                data = json.load(file)
                if not data:
                    click.secho(f"no committee in {filename}", fg="yellow")
                    continue
                com = ScrapeCommittee(**data)
                # do person matching on import so that diffs work
                for member in com.members:
                    mid = self.person_matcher.match(com.chamber, member.name)
                    if mid:
                        member.person_id = mid
                scraped_data.append(com)
        return scraped_data

    def update_unmatched_names(self) -> None:
        if not self.person_matcher:
            self.person_matcher = PersonMatcher(self.abbr)

        # find all committees with unmatched names
        for coms_for_chamber in self.coms_by_parent_and_name.values():
            for com in coms_for_chamber.values():
                updated_count = 0
                for membership in com.members:
                    if not membership.person_id:
                        # do the matching
                        mid = self.person_matcher.match(com.chamber, membership.name)
                        if mid:
                            membership.person_id = mid
                            updated_count += 1
                if updated_count:
                    self.save_committee(com)
                    click.secho(
                        f"updated {updated_count} memberships on {com.name} with names",
                        fg="yellow",
                    )

    def get_merge_plan_by_parent(
        self, parent: str, new_data: list[ScrapeCommittee]
    ) -> DirectoryMergePlan:
        existing_names = set(self.coms_by_parent_and_name[parent].keys())
        new_names = {com.name for com in new_data}
        parent_names = {
            c.id: c.name for c in self.coms_by_parent_and_name[parent].values()
        }

        names_to_add = new_names - existing_names
        names_to_remove = existing_names - new_names
        names_to_compare = new_names & existing_names
        to_merge = list()
        same = 0

        for com in new_data:
            if com.name in names_to_compare:
                # reverse a saved Committee to a ScrapeCommittee for comparison
                existing = self.coms_by_parent_and_name[parent][com.name]
                com_without_id = existing.dict()
                if com_without_id["parent"]:
                    com_without_id["parent"] = parent_names[com_without_id["parent"]]
                com_without_id.pop("id")
                com_without_id.pop("jurisdiction")
                rev_sc = ScrapeCommittee(**com_without_id)
                if com != rev_sc and com.parent == rev_sc.parent:
                    to_merge.append((existing, com))
                else:
                    same += 1

        return DirectoryMergePlan(
            names_to_add=names_to_add,
            names_to_remove=names_to_remove,
            same=same,
            to_merge=to_merge,
        )

    def to_database(self, purge: bool) -> None:
        from openstates.data.models import Organization

        ids = set()
        created_count = 0
        updated_count = 0
        name_change_count = 0

        jurisdiction_id = lookup(abbr=self.abbr).jurisdiction_id
        existing_ids = set(
            Organization.objects.filter(
                jurisdiction_id=jurisdiction_id,
                classification__in=("committee", "subcommittee"),
            ).values_list("id", flat=True)
        )

        for parent, committees in self.coms_by_parent_and_name.items():
            # this sorted hack ensures subcommittees are processed after all committees
            for name, committee in sorted(
                committees.items(), key=lambda c: c[1].parent or ""
            ):
                ids.add(committee.id)
                created, updated, name_changed = committee_to_db(committee)

                if created:
                    click.secho(f"created committee {name}", fg="cyan", bold=True)
                    created_count += 1
                elif updated:
                    click.secho(f"updated committee {name}", fg="cyan")
                    updated_count += 1

                if name_changed:
                    name_change_count += 1

        missing_ids = existing_ids - ids

        # ids that are missing need to be purged
        if missing_ids and not purge:
            click.secho(
                f"{len(missing_ids)} went missing, run with --purge to remove", fg="red"
            )
            for id in missing_ids:
                mobj = Organization.objects.get(pk=id)
                click.secho(f"  {id}: {mobj}")
            raise CancelTransaction()
        elif missing_ids and purge:
            click.secho(f"{len(missing_ids)} purged", fg="yellow")
            Organization.objects.filter(id__in=missing_ids).delete()

        click.secho(
            f"processed {len(ids)} committees, {created_count} created, "
            f"{updated_count} updated"
            f" {name_change_count} name changed",
            fg="green",
        )


@click.group()
def main() -> None:
    pass


@main.command()  # pragma: no cover
@click.argument("abbr")
@click.argument("input_dir")
@click.option("--interactive/--no-interactive", default=False)
def merge(abbr: str, input_dir: str, interactive: bool) -> None:
    """
    Merge scraped committee data into repo.
    """
    comdir = CommitteeDir(abbr)

    coms_by_parent: defaultdict[str, list[ScrapeCommittee]] = defaultdict(list)
    scraped_data = comdir.ingest_scraped_json(input_dir)
    for com in scraped_data:
        coms_by_parent[com.parent or com.chamber].append(com)

    for parent, coms in coms_by_parent.items():
        plan = comdir.get_merge_plan_by_parent(parent, coms)

        click.secho(
            f"{len(plan.names_to_add)} to add",
            fg="yellow" if plan.names_to_add else "green",
        )
        click.secho(
            f"{len(plan.names_to_remove)} to remove",
            fg="yellow" if plan.names_to_remove else "green",
        )
        click.secho(f"{plan.same} without changes", fg="green")
        click.secho(
            f"{len(plan.to_merge)} with changes",
            fg="yellow" if plan.to_merge else "green",
        )

        if plan.names_to_add or plan.names_to_remove or plan.to_merge:
            if interactive and not click.confirm("Do you wish to continue?"):
                sys.exit(1)

            # add new committees
            # sort key ensures parents are added before children
            for com in sorted(coms, key=lambda c: c.parent or ""):
                if com.name in plan.names_to_add:
                    comdir.add_committee(com)
                    click.secho(f"  adding {com.chamber} {com.name}")

            # remove old committees
            for name in plan.names_to_remove:
                filename = comdir.get_filename_by_name(parent, name)
                click.secho(f"removing {filename}", fg="red")
                filename.unlink()

            # merge remaining committees
            for orig, new in plan.to_merge:
                merged = comdir.merge_committees(orig, new)
                comdir.save_committee(merged)
        else:
            click.secho("nothing to do!", fg="green")


@main.command()  # pragma: no cover
@click.argument("abbreviations", nargs=-1)
@click.option(
    "--fix/--no-fix", default=False, help="Enable/disable automatic fixing of data."
)
def lint(abbreviations: list[str], fix: bool) -> None:
    """
    Lint committee YAML files.
    """
    if not abbreviations:
        abbreviations = get_all_abbreviations()

    for abbr in abbreviations:
        comdir = CommitteeDir(abbr, raise_errors=False)
        errors = 0
        click.secho(f"==== {abbr} ====")
        for filename, error in comdir.errors:
            click.secho(filename.name)
            for err in error.errors():
                click.secho(
                    f"  {'.'.join(str(l) for l in err['loc'])}: {err['msg']}", fg="red"
                )
                errors += 1
        if fix:
            comdir.update_unmatched_names()
        comdir.print_warnings()
        if errors:
            click.secho(f"exiting with {errors} errors", fg="red")
            sys.exit(1)


@main.command()
@click.argument("abbreviations", nargs=-1)
@click.option(
    "--purge/--no-purge",
    default=False,
    help="Purge all committees from DB that aren't in YAML.",
)
@click.option(
    "--safe/--no-safe",
    default=False,
    help="Operate in safe mode, no changes will be written to database.",
)
def to_database(abbreviations: list[str], purge: bool, safe: bool) -> None:
    """
    Sync YAML files to DB.
    """
    init_django()

    if not abbreviations:
        abbreviations = get_all_abbreviations()

    for abbr in abbreviations:
        click.secho("==== {} ====".format(abbr), bold=True)
        comdir = CommitteeDir(abbr)

        if safe:
            click.secho("running in safe mode, no changes will be made", fg="magenta")

        try:
            with transaction.atomic():
                comdir.to_database(purge=purge)
                if safe:
                    click.secho("ran in safe mode, no changes were made", fg="magenta")
                    raise CancelTransaction()
        except CancelTransaction:
            sys.exit(1)


if __name__ == "__main__":
    main()
