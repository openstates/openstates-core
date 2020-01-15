import attr
import typing


@attr.s
class District:
    name = attr.ib()
    chamber_type = attr.ib()
    num_seats = attr.ib(default=1)
    division_id = attr.ib()

    @division_id.default
    def _default_div_id(self):
        # default is parent/sld[ul]:prefix
        prefix = "sldl" if self.chamber_type == "lower" else "sldu"
        slug = self.name.lower().replace(" ", "_")
        return f"TODOparent/{prefix}:{slug}"


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
    division_id: str
    jurisdiction_id: str
    url: str
    lower: Chamber = None
    upper: Chamber = None
    legislature: Chamber = None


def simple_numbered_districts(chamber_type, total, *, num_seats=1):
    return [District(str(n), chamber_type, num_seats) for n in range(1, total + 1)]
