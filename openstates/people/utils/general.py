import re
import os
import uuid
import typing
import yaml
from pathlib import Path
from enum import Enum
from collections import defaultdict
from yaml.representer import Representer
from pydantic import BaseModel
from openstates import metadata

# set up defaultdict representation
yaml.add_representer(defaultdict, Representer.represent_dict)
yaml.add_multi_representer(Enum, Representer.represent_str)


def ocd_uuid(type: str) -> str:
    return "ocd-{}/{}".format(type, uuid.uuid4())


def get_data_path(abbr: str) -> Path:
    # there are two options for where the people utilities look for their data:

    if "OS_PEOPLE_DIRECTORY" in os.environ:
        # 1. use the environment variable OS_PEOPLE_DIRECTORY
        base_dir = Path(os.environ["OS_PEOPLE_DIRECTORY"])
    else:
        # 2. if not set, we'll look in a sibling directory
        # this is a nice fallback for local development, but not intended to work
        # in production environments
        sibling_directory = Path(__file__).parents[4] / "people"
        if sibling_directory.exists():
            base_dir = sibling_directory

    print(base_dir)

    # data path is the base directory's data/{abbr} subdirectory
    return base_dir / "data" / abbr


def get_all_abbreviations() -> list[str]:
    return sorted(x.name for x in (Path(__file__).parents[3] / "data").iterdir())


def dump_obj(
    obj: typing.Union[dict, BaseModel],
    *,
    output_dir: typing.Optional[Path] = None,
    filename: typing.Union[Path, str, None] = None,
) -> None:
    if isinstance(obj, BaseModel):
        obj = obj.to_dict()
    if output_dir:
        filename = output_dir / get_new_filename(obj)
    if not filename:
        raise ValueError("must provide output_dir or filename parameter")
    with open(filename, "w") as f:
        yaml.safe_dump(
            obj,
            f,
            default_flow_style=False,
            sort_keys=False,
        )


def get_new_filename(obj: dict) -> str:
    id = obj["id"].split("/")[1]
    name = obj["name"]
    name = re.sub(r"\s+", "-", name)
    name = re.sub(r"[^a-zA-Z-]", "", name)
    return f"{name}-{id}.yml"


def legacy_districts(
    abbr: typing.Optional[str] = None, jurisdiction_id: typing.Optional[str] = None
) -> dict[str, list[str]]:
    """ can take jurisdiction_id or abbr via kwargs """
    legacy_districts: dict[str, list[str]] = {"upper": [], "lower": []}
    for d in metadata.lookup(
        abbr=abbr, jurisdiction_id=jurisdiction_id
    ).legacy_districts:
        legacy_districts[d.chamber_type].append(d.name)
    return legacy_districts


def load_municipalities(abbr: str) -> list[dict]:
    try:
        with open(get_data_path(abbr) / "municipalities.yml") as f:
            return typing.cast(list, yaml.safe_load(f))
    except FileNotFoundError:
        return []
