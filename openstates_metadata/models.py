import attr
import typing


@attr.s(auto_attribs=True)
class District:
    name: str
    num_seats: int = 1
    division_id: str = None


@attr.s(auto_attribs=True)
class Chamber:
    chamber_type: str
    name: str
    title: str
    num_seats: int
    districts: typing.List[District]


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


def simple_numbered_districts(total, *, num_seats=1):
    return [District(str(n), num_seats) for n in range(1, total + 1)]
