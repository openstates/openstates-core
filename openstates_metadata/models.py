import attr
import typing


@attr.s(auto_attribs=True)
class Chamber:
    chamber_type: str
    name: str
    title: str
    num_seats: int
    seats: typing.Mapping[str, int]
    division_ids: typing.Mapping[str, str]


@attr.s(auto_attribs=True)
class State:
    name: str
    abbr: str
    capital: str
    capital_tz: str
    fips: str
    unicameral: bool
    legislature_name: str
    lower: Chamber = None
    upper: Chamber = None
    legislature: Chamber = None
