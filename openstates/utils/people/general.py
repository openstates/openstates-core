import re
import os
import uuid
import typing
import yaml
from pathlib import Path
from enum import Enum
from ... import metadata
from ...models.common import BaseModel


class EnumDumper(yaml.SafeDumper):
    def represent_data(self, data):  # type: ignore
        if isinstance(data, Enum):
            return self.represent_data(data.value)
        return super().represent_data(data)


def ocd_uuid(type: str) -> str:
    return "ocd-{}/{}".format(type, uuid.uuid4())


def get_base_path() -> Path:
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
        else:
            raise EnvironmentError(
                "could not find openstates/people checkout, set OS_PEOPLE_DIRECTORY env variable"
            )

    if not (base_dir / "data").exists():
        raise EnvironmentError(
            f"{base_dir}/data does not exist, check OS_PEOPLE_DIRECTORY"
        )

    return base_dir


def get_data_path(abbr: str) -> Path:
    return get_base_path() / "data" / abbr


def get_all_abbreviations() -> list[str]:
    return sorted(x.name for x in (get_base_path() / "data").iterdir())


def dump_obj(
    obj: BaseModel,
    *,
    output_dir: typing.Optional[Path] = None,
    filename: typing.Union[Path, str, None] = None,
) -> None:
    obj_dict = obj.to_dict()
    if output_dir:
        filename = output_dir / get_new_filename(obj_dict)
    if not filename:
        raise ValueError("must provide output_dir or filename parameter")
    with open(filename, "w") as f:
        yaml.dump(
            obj_dict,
            f,
            default_flow_style=False,
            sort_keys=False,
            Dumper=EnumDumper,
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
