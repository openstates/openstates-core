import typing
from enum import Enum
from pydantic import validator, root_validator
from .common import (
    BaseModel,
    ORG_ID_RE,
    Link,
    OtherName,
    validate_ocd_person,
    validate_ocd_jurisdiction,
    validate_str_no_newline,
)

COMMITTEE_PARENTS = ("upper", "lower", "legislature")


class CommitteeType(str, Enum):
    COMMITTEE = "committee"
    SUBCOMMITTEE = "subcommittee"


class Membership(BaseModel):
    name: str
    role: str
    person_id: typing.Optional[str] = None

    _validate_person_id = validator("person_id", allow_reuse=True)(validate_ocd_person)


class ScrapeCommittee(BaseModel):
    name: str
    parent: str
    classification: CommitteeType = CommitteeType.COMMITTEE
    sources: typing.List[Link] = []
    links: typing.List[Link] = []
    other_names: typing.List[OtherName] = []
    members: typing.List[Membership] = []
    extras: dict = {}

    _validate_strs = validator("name", allow_reuse=True)(validate_str_no_newline)

    @root_validator
    def validate_parent_and_classification(
        cls, values: dict[str, typing.Any]
    ) -> dict[str, typing.Any]:
        if (
            values.get("classification") == "subcommittee"
            and values.get("parent") in COMMITTEE_PARENTS
        ):
            raise ValueError("subcommittees must have a committee parent")
        if (
            values.get("classification") == "committee"
            and values.get("parent") not in COMMITTEE_PARENTS
        ):
            raise ValueError(f"committees must have a parent in {COMMITTEE_PARENTS}")
        return values

    def add_member(self, name: str, role: str = "member") -> None:
        self.members.append(Membership(name=name, role=role))

    def add_link(self, url: str, note: str = "") -> None:
        self.links.append(Link(url=url, note=note))

    def add_source(self, url: str, note: str = "") -> None:
        self.sources.append(Link(url=url, note=note))


class Committee(ScrapeCommittee):
    id: str
    jurisdiction: str

    _validate_jurisdiction = validator("jurisdiction", allow_reuse=True)(
        validate_ocd_jurisdiction
    )

    @validator("id")
    def valid_ocd_org_format(cls, v: str) -> str:
        if not ORG_ID_RE.match(v):
            raise ValueError("must match ocd-organization/UUID format")
        return v

    def to_dict(self) -> dict[str, typing.Any]:
        # hack to always have id on top
        return {
            "id": self.id,
            "jurisdiction": self.jurisdiction,
            **super().dict(exclude_defaults=True),
        }
