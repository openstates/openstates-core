import typing
import re
import json
import click
import copy
import datetime
from pathlib import Path
from pydantic import BaseModel
from ... import metadata
from ..people import (
    get_new_filename,
    get_data_path,
    dump_obj,
    ocd_uuid,
    retire_person,
    retire_file,
)
from ...models.people import (
    Person,
    Role,
    Party,
    Office,
    Link,
    OtherName,
    OtherIdentifier,
)


def find_file(leg_id: str, *, state: str = "*") -> Path:
    if leg_id.startswith("ocd-person"):
        leg_id = leg_id.split("/")[1]
    assert len(leg_id) == 36

    if state == "*":
        filedir = get_data_path(".")
        files = list(filedir.glob(f"*/*/*{leg_id}.yml"))
    else:
        filedir = get_data_path(state)
        files = list(filedir.glob(f"*/*{leg_id}.yml"))

    if len(files) == 1:
        return files[0]
    elif len(files) > 1:
        raise ValueError(f"multiple files with same leg_id: {leg_id}")
    else:
        raise FileNotFoundError()


def collapse_duplicates(offices: list[Office]) -> list[Office]:
    output_offices = []
    used_offices: set[int] = set()

    for i, office1 in enumerate(offices):
        if i in used_offices:
            continue
        for j, office2 in enumerate(offices):
            if j in used_offices or i == j:
                continue
            # can one subsume the other?
            office1_wins = all(
                (
                    office1.voice == office2.voice or office2.voice == "",
                    office1.fax == office2.fax or office2.fax == "",
                    office1.address == office2.address or office2.address == "",
                )
            )
            office2_wins = all(
                (
                    office1.voice == office2.voice or office1.voice == "",
                    office1.fax == office2.fax or office1.fax == "",
                    office1.address == office2.address or office1.address == "",
                )
            )
            # if both are the same except the name, the one with the name wins
            if office1_wins and office2_wins:
                if office1.name:
                    office2_wins = False
                elif office2.name:
                    office1_wins = False

            if office1_wins:
                output_offices.append(office1)
                used_offices.update((i, j))
                break
            elif office2_wins:
                output_offices.append(office2)
                used_offices.update((i, j))
                break

        if i not in used_offices:
            output_offices.append(office1)
            used_offices.add(i)

    return output_offices


def merge_parties(old: list[Party], new: list[Party]) -> typing.Optional[list[Party]]:
    # only works for one new party for now, other cases aren't needed yet
    if len(new) > 1:
        raise ValueError(f"invalid new party config: {new}")
    if old[-1] == new[0]:
        return None
    retval = copy.deepcopy(old)

    if retval[-1].end_date == "":
        # these dates are imprecise for now
        retval[-1].end_date = datetime.date.today().strftime("%Y-%m-%d")
    retval.append(new[0])
    return retval


def merge_offices(
    old: list[Office], new: list[Office]
) -> typing.Optional[typing.List[Office]]:
    # figure out which office entries are which
    old_offices: dict[str, Office] = {}
    new_offices: dict[str, Office] = {}
    offices = []
    update = False

    for office in old:
        name = office.display_name
        if name not in old_offices:
            old_offices[name] = office
        else:
            raise NotImplementedError(f"extra old {name}")
    for office in new:
        name = office.display_name
        if name not in new_offices:
            new_offices[name] = office
        else:
            raise NotImplementedError(f"extra new {name}")

    for name in sorted(set(old_offices) | set(new_offices)):
        combined = update_office(old_offices.get(name), new_offices.get(name))
        offices.append(combined)
        if combined != old_offices.get(name):
            update = True

    # return all offices if there were any changes
    if update:
        return collapse_duplicates(offices)
    else:
        return None


def update_office(
    old_office: typing.Optional[Office],
    new_office: typing.Optional[Office],
) -> Office:
    """function returns a copy of old_office updated with values from new if applicable"""

    # if only one exists, return that one
    if not old_office and new_office:
        return new_office
    if not new_office and old_office:
        return old_office

    # combine the two
    if new_office and old_office:
        updated_office = old_office.copy()
        for field in updated_office.__fields__.keys():
            oldval = getattr(old_office, field)
            newval = getattr(new_office, field)
            if oldval != newval and newval:
                setattr(updated_office, field, newval)
    return updated_office


class Append:
    def __init__(self, key_name: str, list_item: typing.Any):
        self.key_name = key_name
        self.list_item = list_item

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Append)
            and self.key_name == other.key_name
            and self.list_item == other.list_item
        )

    def __str__(self) -> str:
        return f"{self.key_name}: append {dict(self.list_item)}"

    def __repr__(self) -> str:
        return f"Append({self.key_name}, {self.list_item})"


class Replace:
    def __init__(self, key_name: str, value_one: typing.Any, value_two: typing.Any):
        self.key_name = key_name
        self.value_one = value_one
        self.value_two = value_two

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Replace)
            and self.key_name == other.key_name
            and self.value_one == other.value_one
            and self.value_two == other.value_two
        )

    def __str__(self) -> str:
        return f"{self.key_name}: {self.value_one} => {self.value_two}"

    def __repr__(self) -> str:
        return f"Replace({self.key_name}, {self.value_one}, {self.value_two})"


class OfficesReplace(Replace):
    def __str__(self) -> str:
        def _fmt_cd(cd: Office) -> str:
            cd_str = f"{cd.display_name}"
            for key in ("address", "voice", "fax"):
                if val := getattr(cd, key):
                    cd_str += f" {key}={val}"
            return cd_str

        old = "\n\t".join(_fmt_cd(cd) for cd in self.value_one)
        new = "\n\t".join(_fmt_cd(cd) for cd in self.value_two)

        return f"{self.key_name} changed from: \n\t{old}\n  to\n\t{new}"


def compute_merge(
    obj1: BaseModel,
    obj2: BaseModel,
    prefix: str = "",
    keep_both_ids: bool = False,
    reset_offices: bool = False,
) -> list[typing.Union[Append, Replace]]:
    all_keys = obj1.__fields__.keys()
    changes: list[typing.Union[Append, Replace]] = []

    for key in all_keys:
        key_name = ".".join((prefix, key)) if prefix else key
        val1 = getattr(obj1, key)
        val2 = getattr(obj2, key)

        # special cases first
        if key == "id":
            if val1 != val2 and keep_both_ids:
                # old id stays as id: to keep things sane
                changes.append(
                    Append(
                        "other_identifiers",
                        OtherIdentifier(scheme="openstates", identifier=val2),
                    )
                )
        elif key == "name":
            if val1 != val2:
                # new name becomes name, but old name goes into other_names
                changes.append(Append("other_names", OtherName(name=val1)))
                changes.append(Replace("name", val1, val2))
        elif key == "party":
            changed = merge_parties(val1, val2)
            if changed:
                changes.append(Replace("party", val1, changed))
        elif key == "offices":
            if reset_offices:
                changed_offices = val2
            else:
                changed_offices = merge_offices(val1, val2)
            if changed_offices:
                changes.append(OfficesReplace("offices", val1 or [], changed_offices))
        elif isinstance(val1, list) or isinstance(val2, list):
            if val1 and not val2:
                continue
            elif val2 and not val1:
                changes.append(Replace(key_name, val1, val2))
            else:
                # both have elements, append new to old, leave old intact
                for item in typing.cast(list, val2):
                    if item not in typing.cast(list, val1):
                        changes.append(Append(key_name, item))
        elif isinstance(val1, BaseModel) or isinstance(val2, BaseModel):
            changes.extend(compute_merge(val1, val2, prefix=key_name))
        else:
            # if values both exist and differ, or val1 is empty, do a Replace
            if (val1 and val2 and val1 != val2) or (not val1 and val2):
                changes.append(Replace(key_name, val1, val2))

    return changes


def roles_equalish(role1: Role, role2: Role) -> bool:
    return (
        role1.type == role2.type
        and role1.jurisdiction == role2.jurisdiction
        and role1.district == role2.district
        and role1.end_date == role2.end_date
        and role1.end_reason == role2.end_reason
    )


def incoming_merge(
    abbr: str,
    existing_people: list[Person],
    new_people: list[Person],
    retirement: str,
    reset_offices: bool,
) -> list[tuple[Person, list[Person]]]:
    unmatched = []

    seats_for_district = {}
    state = metadata.lookup(abbr=abbr)
    for chamber in state.chambers:
        chtype = (
            "legislature"
            if chamber.chamber_type == "unicameral"
            else chamber.chamber_type
        )
        seats_for_district[chtype] = {
            district.name: district.num_seats for district in chamber.districts
        }

    # find candidate(s) for each new person
    for new in new_people:
        matched = False
        role_matches = []

        for existing in existing_people:
            name_match = new.name == existing.name
            role_match = False
            for role in existing.roles:
                if role.type == "mayor" or role.type == "governor":
                    continue
                seats = seats_for_district[role.type].get(
                    typing.cast(str, role.district), 1
                )
                # roles match if they are equal and there's only one seat, or
                # if there is already a name match on this legislator
                if roles_equalish(new.roles[0], role) and (seats == 1 or name_match):
                    role_match = True
                    # if they match without start date, copy the start date over so it isn't
                    # altered or otherwise removed in the merge
                    new.roles[0] = role
                    break
            if name_match or role_match:
                matched = interactive_merge(
                    abbr,
                    existing,
                    new,
                    name_match,
                    role_match,
                    retirement,
                    reset_offices,
                )

            if matched:
                break

            # if we haven't matched and this was a role match, save this for later
            if role_match:
                role_matches.append(existing)
        else:
            # not matched
            unmatched.append((new, role_matches))
            write_new_file(abbr, new, "legislature")

    return unmatched


def write_new_file(abbr: str, new: Person, _type: str) -> None:
    filedir = get_data_path(abbr)
    fname = get_new_filename(new.dict())
    newpath = filedir / _type / fname
    dump_obj(new, filename=newpath)
    click.secho(f"writing {new} to {newpath}", fg="yellow")


def retire(
    existing: Person, new: Person, retirement: typing.Optional[str] = None
) -> None:
    if not retirement:
        retirement = click.prompt("Enter retirement date YYYY-MM-DD")
    person, num = retire_person(existing, typing.cast(str, retirement))
    fname = find_file(existing.id)
    dump_obj(person, filename=fname)
    new_filename = retire_file(fname)
    click.secho(f"moved from {fname} to {new_filename}")


def interactive_merge(
    abbr: str,
    old: Person,
    new: Person,
    name_match: bool,
    role_match: bool,
    retirement: str,
    reset_offices: bool,
) -> bool:
    """
    returns True iff a merge was done
    """
    oldfname = find_file(old.id)
    # click.secho(" {} {}".format(oldfname, newfname), fg="yellow")

    # simulate difference
    changes = compute_merge(old, new, keep_both_ids=False, reset_offices=reset_offices)

    if not changes:
        click.secho(" perfect match", fg="green")
        return True

    for change in changes:
        if change.key_name == "name" or change.key_name == "roles":
            click.secho("    " + str(change), fg="red", bold=True)
        else:
            click.echo("    " + str(change))

    ch = "~"
    if name_match and role_match:
        choices = "m"
        # automatically pick merge
        ch = "m"
        # there is one very specific case that this fails in, if someone is beaten
        # by someone with the exact same name, that'll need to be caught manually
    elif name_match:
        choices = "m"
        text = "(m)erge?"
    elif role_match:
        choices = "mr"
        text = f"(m)erge? (r)etire {old.name}?"

    while ch not in (choices + "sa"):
        click.secho(text + " (s)kip? (a)bort?", bold=True)
        ch = click.getchar()

    if ch == "a":
        raise SystemExit(-1)
    elif ch == "m":
        merged = merge_people(
            old, new, keep_both_ids=False, reset_offices=reset_offices
        )
        dump_obj(merged, filename=oldfname)
        click.secho(" merged.", fg="green")
    elif ch == "r":
        # TODO: remove new file
        write_new_file(abbr, new, "legislature")
        retire(old, new, retirement)
    elif ch == "s":
        return False

    return True


def merge_people(
    old: Person, new: Person, keep_both_ids: bool = False, reset_offices: bool = False
) -> Person:
    """
    Function to merge two people objects.

    keep_both_ids
        Should be set to True iff people have been imported before.
        If we're dealing with an election, it should be set to false since the new ID
        hasn't been published anywhere yet.
    """
    changes = compute_merge(
        old,
        new,
        keep_both_ids=keep_both_ids,
        reset_offices=reset_offices,
    )

    for change in changes:
        if isinstance(change, Replace):
            keys = change.key_name.split(".")

            # recursively set the value based on dotted key
            temp_obj = old
            for key in keys[:-1]:
                temp_obj = getattr(temp_obj, key)
            setattr(temp_obj, keys[-1], change.value_two)
        if isinstance(change, Append):
            getattr(old, change.key_name).append(change.list_item)
    return old


PHONE_RE = re.compile(
    r"""^
                      \D*(1?)\D*                                # prefix
                      (\d{3})\D*(\d{3})\D*(\d{4}).*?             # main 10 digits
                      (?:(?:ext|Ext|EXT)\.?\s*\s*(\d{1,4}))?    # extension
                      $""",
    re.VERBOSE,
)


def reformat_phone_number(phone: str) -> str:
    match = PHONE_RE.match(phone)
    if match:
        groups = match.groups()

        ext = groups[-1]
        if ext:
            ext = f" ext. {ext}"
        else:
            ext = ""

        if not groups[0]:
            groups = groups[1:-1]
        else:
            groups = groups[:-1]
        return "-".join(groups) + ext
    else:
        return phone


def reformat_address(address: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"\s*\n\s*", ";", address))


def process_scrape_dir(input_dir: Path, jurisdiction_id: str) -> list[Person]:
    new_people = []

    # process people
    for filename in input_dir.glob("*.json"):
        with open(filename) as f:
            data = json.load(f)

        person = process_person(data, jurisdiction_id)
        new_people.append(person)

    return new_people


def process_office(office_data: dict) -> typing.Optional[Office]:
    voice = fax = address = ""
    if value := office_data["voice"]:
        voice = reformat_phone_number(value)
    if value := office_data["fax"]:
        fax = reformat_phone_number(value)
    if value := office_data["address"]:
        address = reformat_address(value)

    if voice or fax or address:
        return Office(
            classification=office_data["classification"],
            voice=voice,
            fax=fax,
            address=address,
        )
    else:
        return None


def process_person(data: dict, jurisdiction_id: str) -> Person:
    offices: list[Office] = []
    if office := data.pop("capitol_office"):
        cd = process_office(office)
        if cd:
            offices.append(cd)
    if office := data.pop("district_office"):
        cd = process_office(office)
        if cd:
            offices.append(cd)
    for office in data.pop("additional_offices"):
        cd = process_office(office)
        if cd:
            offices.append(cd)

    data.pop("state")
    chamber = data.pop("chamber")
    district = data.pop("district")

    result = Person(
        id=ocd_uuid("person"),
        roles=[
            Role(
                type=chamber,
                district=str(district),
                jurisdiction=jurisdiction_id,
            )
        ],
        party=[Party(name=data.pop("party"))],
        links=[Link(url=link["url"], note=link["note"]) for link in data.pop("links")],
        sources=[
            Link(url=link["url"], note=link["note"]) for link in data.pop("sources")
        ],
        offices=offices,
        **data,
    )

    return result
