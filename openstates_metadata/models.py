import attr
import typing


@attr.s
class District:
    name = attr.ib()
    chamber_type = attr.ib()
    division_id = attr.ib()
    num_seats = attr.ib(default=1)


@attr.s(auto_attribs=True)
class Chamber:
    chamber_type: str
    name: str
    title: str
    num_seats: int
    organization_id: str
    districts: typing.List[District]

    def lookup_district(self, division_id):
        for d in self.districts:
            if d.division_id == division_id:
                return d


@attr.s(auto_attribs=True)
class State:
    name: str
    abbr: str
    capital: str
    capital_tz: str
    fips: str
    unicameral: bool
    legislature_name: str
    legislature_organization_id: str
    executive_name: str
    executive_organization_id: str
    division_id: str
    jurisdiction_id: str
    url: str
    lower: Chamber = None
    upper: Chamber = None
    legislature: Chamber = None

    @property
    def chambers(self):
        if self.unicameral:
            return [self.legislature]
        else:
            return [self.lower, self.upper]

    @property
    def legacy_districts(self):
        from .data.legacy_districts import legacy_districts

        return legacy_districts.get(self.abbr.lower(), [])

    def lookup_district(self, division_id):
        if self.unicameral:
            return self.legislature.lookup_district(division_id)
        elif "sldl" in division_id:
            return self.lower.lookup_district(division_id)
        elif "sldu" in division_id:
            return self.upper.lookup_district(division_id)


def simple_numbered_districts(parent_id, chamber_type, total, *, num_seats=1):
    prefix = "sldl" if chamber_type == "lower" else "sldu"
    return [
        District(str(n), chamber_type, f"{parent_id}/{prefix}:{n}", num_seats)
        for n in range(1, total + 1)
    ]
