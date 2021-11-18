import typing
from enum import Enum
from pydantic import validator, root_validator
from .common import (
    BaseModel,
    Link,
    OtherName,
    validate_ocd_person,
    validate_ocd_jurisdiction,
    validate_ocd_organization,
    validate_str_no_newline,
)


class CommitteeChamber(str, Enum):
    UPPER = "upper"
    LOWER = "lower"
    LEGISLATURE = "legislature"


class CommitteeType(str, Enum):
    COMMITTEE = "committee"
    SUBCOMMITTEE = "subcommittee"


class Membership(BaseModel):
    name: str
    role: str
    person_id: typing.Optional[str] = None

    _validate_person_id = validator("person_id", allow_reuse=True)(validate_ocd_person)
    _validate_name = validator("name", allow_reuse=True)(validate_str_no_newline)
    _validate_role = validator("role", allow_reuse=True)(validate_str_no_newline)

    @validator("name")
    def not_blank(cls, val: str) -> str:
        val = val.strip()
        if not val:
            raise ValueError("empty name")
        return val


class ScrapeCommittee(BaseModel):
    name: str
    chamber: CommitteeChamber
    classification: CommitteeType = CommitteeType.COMMITTEE
    parent: typing.Optional[str] = None
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
        if values.get("classification") == "subcommittee" and not values.get("parent"):
            raise ValueError("subcommittees must have a parent")
        if values.get("classification") == "committee" and values.get("parent"):
            raise ValueError(
                "committees may not have a parent, set classification=subcommittee"
            )
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
    _validate_id = validator("id", allow_reuse=True)(validate_ocd_organization)
    _validate_parent = validator("parent", allow_reuse=True)(validate_ocd_organization)

    @root_validator
    def validate_has_members(cls, data: dict[str, typing.Any]) -> dict[str, typing.Any]:
        if not len(data.get("members", [])):  # type: ignore
            raise ValueError("committees must have members")
        return data

    def to_dict(self) -> dict[str, typing.Any]:
        # hack to always have id on top & always include classification
        return {
            "id": self.id,
            "jurisdiction": self.jurisdiction,
            "classification": self.classification.value
            if isinstance(self.classification, CommitteeType)
            else self.classification,
            **super().dict(exclude_defaults=True),
        }
